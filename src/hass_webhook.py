import base64
import requests


def send_to_webhook(message, hassUrl, HassWwwFile, webhookName, imagePath):
   
    webhook_url = hassUrl + "/api/webhook/" + webhookName
    hassImageUrl = hassUrl + HassWwwFile  + imagePath

    data = {
        "message": message,
        "motion_image": hassImageUrl
    }
    headers = {"Content-Type": "application/json"}
    requests.post(webhook_url, json=data, headers=headers)

    