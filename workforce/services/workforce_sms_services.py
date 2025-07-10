import requests


def send_bulk_sms(api_key, sender_id, messages):
    """
    Send bulk SMS using bulksmsbd.net API.

    :param api_key: str - Your API key
    :param sender_id: str - Your sender ID
    :param messages: list of dicts - Each dict must have 'to' and 'message' keys
    :return: dict - API response
    """
    url = "http://bulksmsbd.net/api/smsapimany"
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