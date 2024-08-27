import requests
from settings import NTFY_CHANNEL

def send_notification(message):
    print(f"Sending notification: {message}")
    requests.post(f"https://ntfy.sh/{NTFY_CHANNEL}", data=message.encode(encoding='utf-8'))