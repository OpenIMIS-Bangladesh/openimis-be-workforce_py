import requests
import os


def send_sms(messages):
    return send_bulk_sms(messages)


def send_bulk_sms(messages):
    url = os.environ.get("BULKSMS_API_URL")
    api_key = os.environ.get("BULKSMS_API_KEY")
    sender_id = os.environ.get("BULKSMS_SENDER_ID")

    payload = {
        "api_key": api_key,
        "senderid": sender_id,
        "messages": messages
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
