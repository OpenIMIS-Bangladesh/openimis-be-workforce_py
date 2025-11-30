import requests
import os


def send_sms(sms_to, message):
    return send_bulk_sms(sms_to, message)


def send_bulk_sms(sms_to, message):
    url = os.environ.get("SMS_GW_URL")

    payload = {
        "apikey": os.environ.get("SMS_GW_API_KEY"),
        "secretkey": os.environ.get("SMS_GW_SECRET_KEY"),
        "callerID": os.environ.get("SMS_GW_SENDER_ID"),
        "toUser": sms_to,
        "messageContent": message,
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
