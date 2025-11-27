import time
import requests
import json

WEBEX_TOKEN = "OTZkZTUxNTUtM2QyZS00YzdmLWEwY2UtYWMxYzYxYTU1ZTk0ZmNhMThlZGItNjk2_P0A1_13494cac-24b4-4f89-8247-193cc92a7636"
ROOM_ID = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vZGIwODdjYzAtYzlkYy0xMWYwLWE4NmYtNTdlODQ3OWQ4Zjg5"
BOT_MENTION_NAME = "TroublsShootingNotifierBot2"
LAST_MESSAGE_ID = None

SERVICENOW_INSTANCE = "https://dev210569.service-now.com/"
SERVICENOW_USER = "admin"
SERVICENOW_PASSWORD = "=/kb3tG7VyUL"

# ------------------------------------------------
# Get bot ID (to avoid reacting to itself)
# ------------------------------------------------
def get_bot_id():
    url = "https://webexapis.com/v1/people/me"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
    )
    return response.json()["id"]

BOT_ID = get_bot_id()
print("Bot ID:", BOT_ID)


# ------------------------------------------------
# Create ServiceNow Incident
# ------------------------------------------------
def create_incident(short_description, description):
    url = f"{SERVICENOW_INSTANCE}/api/now/table/incident"
    payload = {
        "short_description": short_description,
        "description": description
    }

    response = requests.post(
        url,
        auth=(SERVICENOW_USER, SERVICENOW_PASSWORD),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        data=json.dumps(payload)
    )

    if response.status_code == 201:
        return response.json()["result"]["number"]
    return None


def send_message(text):
    url = "https://webexapis.com/v1/messages"
    requests.post(
        url,
        headers={"Authorization": f"Bearer {WEBEX_TOKEN}"},
        json={"roomId": ROOM_ID, "text": text}
    )


print("Bot polling started and listening to HUMAN messages…")

while True:
    url = f"https://webexapis.com/v1/messages?roomId={ROOM_ID}&mentionedPeople=me&max=1"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
    )

    messages = response.json().get("items", [])

    if not messages:
        time.sleep(1)
        continue

    msg = messages[0]
    msgId = msg["id"]
    msgText = msg.get("text") or msg.get("markdown") or ""
    msgText = msgText.strip()
    msgFrom = msg.get("personId")
    print()
    print("MESSAGE FROM:", msgFrom) 
    print()
    print("DEBUG RAW MESSAGE:", msg)
    print("DEBUG TEXT:", msgText)
    print()


    # 1) Ignore if message same as the one we already processed
    if msgId == LAST_MESSAGE_ID:
        time.sleep(1)
        continue

    # 2) Ignore messages written by the bot itself
    if msgFrom == BOT_ID:
        LAST_MESSAGE_ID = msgId
        time.sleep(1)
        continue

    # If we reach here → a NEW HUMAN message!
    print("Human wrote:", msgText)
    LAST_MESSAGE_ID = msgId

    # ==============================
    # Example logic:
    # ==============================

    if "vpn" in msgText.lower():
        ticket = create_incident("VPN Issue", msgText)
        send_message(f"ServiceNow ticket created: {ticket}")

    else:
        ticket = create_incident("General IT Issue", msgText)
        send_message(f"Ticket Created: {ticket}")

    print("Recheck")
    time.sleep(1)
