import requests

TOPIC_NAME = 'habit-mgr-1' # Change this to your own topic name, otherwise you will receive notifications for all users

def send_notification(message):
    print(f"Sending notification: {message}")
    requests.post(f"https://ntfy.sh/{TOPIC_NAME}", data=message.encode(encoding='utf-8'))