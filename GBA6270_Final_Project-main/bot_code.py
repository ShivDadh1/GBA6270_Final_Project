#!/usr/bin/env python3
"""
WebEx -> spaCy NLP -> ServiceNow Incident Automation Bot
Placeholders and environment variables are used for credentials and tokens.
See README.md for setup and deployment instructions.
"""

import os
import time
import logging
import requests
import json
from spacy_module import classify_message, extract_entities

# Configuration from environment variables (DO NOT hardcode credentials)
WEBEX_TOKEN = os.getenv("WEBEX_TOKEN")
ROOM_ID = os.getenv("ROOM_ID")
SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")  # e.g. https://devXXXXX.service-now.com
SERVICENOW_USER = os.getenv("SERVICENOW_USER")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))  # seconds

if not WEBEX_TOKEN or not ROOM_ID or not SERVICENOW_INSTANCE or not SERVICENOW_USER or not SERVICENOW_PASSWORD:
    raise SystemExit("Missing required environment variables. See README.md for required vars.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_bot_id():
    url = "https://webexapis.com/v1/people/me"
    resp = requests.get(url, headers={"Authorization": f"Bearer {WEBEX_TOKEN}"})
    resp.raise_for_status()
    return resp.json()["id"]

def fetch_latest_message(mentioned_only=True):
    params = {"roomId": ROOM_ID, "max": 1}
    if mentioned_only:
        params["mentionedPeople"] = "me"
    url = "https://webexapis.com/v1/messages"
    resp = requests.get(url, headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    return items[0] if items else None

def create_servicenow_incident(short_description, description, category=None, subcategory=None, impact="2", urgency="2", priority="3"):
    #url = f"{SERVICENOW_INSTANCE.rstrip('/')}/api/now/table/incident"
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    logging.info(url)
    payload = {
        "short_description": short_description,
        "description": description,
        "category": category or "inquiry",
        "subcategory": subcategory or "general",
        "impact": impact,
        "urgency": urgency,
        "priority": priority
    }
    logging.info(SERVICENOW_USER)
    logging.info(SERVICENOW_PASSWORD)
    resp = requests.post(url, auth=(SERVICENOW_USER, SERVICENOW_PASSWORD),
                         headers={"Content-Type": "application/json", "Accept": "application/json"},
                         data=json.dumps(payload), timeout=10)
    if resp.status_code in (200, 201):
        return resp.json().get("result", {})
    else:
        logging.error("ServiceNow error %s: %s", resp.status_code, resp.text)
        return None

def send_webex_message(text):
    url = "https://webexapis.com/v1/messages"
    resp = requests.post(url, headers={"Authorization": f"Bearer {WEBEX_TOKEN}", "Content-Type":"application/json"},
                         json={"roomId": ROOM_ID, "text": text}, timeout=10)
    resp.raise_for_status()
    return resp.json()

def main():
    logging.info("Starting bot...")
    bot_id = get_bot_id()
    logging.info("Bot id: %s", bot_id)
    last_message_id = None

    while True:
        try:
            msg = fetch_latest_message(mentioned_only=True)
            if not msg:
                time.sleep(POLL_INTERVAL)
                continue

            msg_id = msg.get("id")
            msg_from = msg.get("personId")
            msg_text = (msg.get("text") or msg.get("markdown") or "").strip()

            if msg_id == last_message_id:
                time.sleep(POLL_INTERVAL)
                continue

            # Ignore messages from bot itself
            if msg_from == bot_id:
                last_message_id = msg_id
                time.sleep(POLL_INTERVAL)
                continue

            logging.info("New human message: %s", msg_text)
            last_message_id = msg_id

            # Analyze with spaCy
            category = classify_message(msg_text)
            entities = extract_entities(msg_text)
            priority_map = {"critical": "1", "high": "2", "medium": "3", "low": "4"}
            urgency = priority_map.get(category.lower(), "3")

            short_desc = f"[{category}] {msg_text[:80]}"
            detailed_desc = f"Message: {msg_text}\\nDetected entities: {entities}"

            # Create ServiceNow ticket
            sn_result = create_servicenow_incident(short_desc, detailed_desc, category=category, subcategory="auto", impact="2", urgency=urgency, priority=urgency)
            if sn_result:
                ticket_number = sn_result.get("number", "UNKNOWN")
                send_webex_message(f"Ticket created: {ticket_number} (category: {category})")
                logging.info("Created ticket %s for message %s", ticket_number, msg_id)
            else:
                print(msg_text)
                send_webex_message("Failed to create ServiceNow ticket. Please check logs.")

        except requests.exceptions.RequestException as e:
            logging.exception("Network/API error: %s", e)
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully")
            break
        except Exception as e:
            logging.exception("Unexpected error: %s", e)
            time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
