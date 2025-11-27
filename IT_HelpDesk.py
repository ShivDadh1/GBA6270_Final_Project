import requests
import json
import time

ROOMID = "a0c473e0-a7d4-11f0-90ed-d91235fcbbf8"
TOKEN = "ZDg5YzhhNTktZWNkOC00M2E1LTliNzItNDhmYmVhY2M4NzQxZjAwMDA5NzEtYTNk_P0A1_e58072af-9d57-4b13-abf7-eb3b506c964d"
def connect2web():

    URL = f"https://webexapis.com/v1/messages?roomId={ROOMID}&max=1"

    header = {"Authorization": f"Bearer {TOKEN}", 
                    "Accept": "application/json"}

    result = requests.get(URL, headers=header)
        
    if not result.status_code == 200:
        print("Connection failed. Status code: {} . Text: {}".format(result.status_code, result.text))
        return None, None
            
    return result.json()["items"][0]

def get_bot_id():

    url = "https://webexapis.com/v1/people/me"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()["id"]

    
def create_incident(short_description, description):

    SERVICENOW_INSTANCE = "https://dev210569.service-now.com/"
    SERVICENOW_USER = "admin"
    SERVICENOW_PASSWORD = "=/kb3tG7VyUL"

    url = f"{SERVICENOW_INSTANCE}/api/now/table/incident"

    payload = {
        "short_description": short_description,
        "description": description,
        "category": "network",
        "subcategory": "connectivity",
        "impact": "2",
        "urgency": "2",
        "priority": "3"
    }

    response = requests.post(
        url,
        auth=(SERVICENOW_USER, SERVICENOW_PASSWORD),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        data=json.dumps(payload)
    )

    if response.status_code == 201:
        result = response.json()["result"]
        print(result["number"])
        return {
            "ticket_number": result["number"],
            "sys_id": result["sys_id"]
        }
    else:
        print("ServiceNow Error:", response.status_code, response.text)
        return None

def main():
    
    LAST_MESSAGE_ID = ''

    while True:
        message = connect2web() 
        
        if message is None:
            time.sleep(1)
            continue

        msgId = message.get("id")
        msgText = message.get("text") or message.get("markdown") or ""
        msgText = msgText.strip()
        msgFrom = message.get("personId")

        print()
        print("MESSAGE FROM:", msgFrom) 
        print()
        print("DEBUG RAW MESSAGE:", message)
        print("DEBUG TEXT:", msgText)


        # 1) Ignore if message same as the one we already processed
        if msgId == LAST_MESSAGE_ID:
            time.sleep(1)
            continue

        BOT_ID = get_bot_id()  

        # 2) Ignore messages written by the bot itself
        if msgFrom == BOT_ID:
            LAST_MESSAGE_ID = msgId
            time.sleep(1)
            continue

        # If we reach here → a NEW HUMAN message!
        print("Human wrote:", msgText)
        LAST_MESSAGE_ID = msgId

        #fix this logic
       

        #spaCY implementation 
        create_incident("Undetected Webex Issue", message)


        time.sleep(1)
main()