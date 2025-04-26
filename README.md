## Tuya Image Processing and HASS Webhook Notification
This project allows you to process images from your Tuya WiFi peephole camera and send notifications to your Home Assistant (HASS) instance via webhook.

The idea for this project was inspired by a post from Belzedaar Paul (https://community.home-assistant.io/t/make-the-picture-taken-from-tuya-smart-video-doorbell-available-in-ha/362848/23) and a script from WattageGuy's repository (https://github.com/WattageGuy/My-Home-Assistant-Config/blob/main/tuya-doorbell/app.py).

## Description
By default, the script looks for the ipc_motion and 185 value, which contains the decoded file path. If your device uses a different DPID, you can replace the settings in the .env file.

## Getting Started
To use this script, follow these steps:

1. Enable messaging in the Tuya IoT project page
2. Authorize the API using the Beta API
3. If the script fails with an "API unauthorized" error, open a case on the Tuya webpage
4. Rename the .env-example file to .env and fill in your details
5. Install all dependencies from the requirements.txt file and run main.py
