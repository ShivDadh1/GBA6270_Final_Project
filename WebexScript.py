# Add Comment 1

import requests
import json

url = "https://webexapis.com/v1/messages"
maxInt = (int)(1)

roomId= "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vZGIwODdjYzAtYzlkYy0xMWYwLWE4NmYtNTdlODQ3OWQ4Zjg5"
webexToken = "OGM1ZjI2N2QtNWRkNS00MzQ5LWI5YjItMDdkNmJjMGYwNDVjNmU5ZDJiNmUtY2Fj_P0A1_13494cac-24b4-4f89-8247-193cc92a7636"

result = requests.get( f"{url}?roomId={roomId}&max={maxInt}", headers = {"Authorization": f"Bearer {webexToken}", "Accept": "application/json"})


if not result.status_code == 200:
    raise Exception("Connection failed. Status code: {} . Text: {}".format(result.status_code, result.text))

message = result.json()
print(message)


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
    


ticket_desc = result.json()['items'][0]['text']
print(ticket_desc)

create_incident("Undetected Webex Issue", ticket_desc)