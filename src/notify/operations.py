import requests


def send_notification(slack_webhook_url, **data):
    response = requests.post(url=slack_webhook_url, json=data)
    return response.text
