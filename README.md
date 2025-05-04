## Tuya Image Processing and HASS Webhook Notification
This project allows you to process images from your Tuya WiFi peephole camera and send notifications to your Home Assistant (HASS) instance via webhook.

The idea for this project was inspired by a post from Belzedaar Paul (https://community.home-assistant.io/t/make-the-picture-taken-from-tuya-smart-video-doorbell-available-in-ha/362848/23) and a script from WattageGuy's repository (https://github.com/WattageGuy/My-Home-Assistant-Config/blob/main/tuya-doorbell/app.py).

## Description
By default, the script looks for the ipc_motion and 185 value, which contains the decoded file path. If your device uses a different DPID, you can replace the settings in the .env file. 


### How It Works:
1. **Today's Files**: Files created today are left untouched in the root folder.
2. **Older Files**: Files older than today are moved into subfolders based on their creation date:
   - **Year**: A folder is created for the year of the file's creation.
   - **Month**: Inside the year folder, a subfolder is created for the month.
   - **Day**: Inside the month folder, a subfolder is created for the day.


## Getting Started
To use this script, follow these steps:

1. Enable messaging in the Tuya IoT project page
2. Authorize the API using the Beta API
3. If the script fails with an "API unauthorized" error, open a case on the Tuya webpage
4. Rename the .env-example file to .env and fill in your details
5. Install all dependencies from the requirements.txt file and run main.py

## Service Creation
To create a service for this script, follow these steps:

1. Create a new systemd service file:
    ```bash
    sudo nano /etc/systemd/system/tuya_image_processing.service
    ```

2. Add the following content to the file:
    ```ini
    [Unit]
    Description=Tuya Image Processing Service
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /path/to/your/script/main.py
    WorkingDirectory=/path/to/your/script
    EnvironmentFile=/path/to/your/script/.env
    Restart=always
    User=your-username

    [Install]
    WantedBy=multi-user.target
    ```

    Replace `/path/to/your/script` with the actual path to your script and `your-username` with the user running the service.

3. Reload the systemd daemon to recognize the new service:
    ```bash
    sudo systemctl daemon-reload
    ```

4. Enable the service to start on boot:
    ```bash
    sudo systemctl enable tuya_image_processing.service
    ```

5. Start the service:
    ```bash
    sudo systemctl start tuya_image_processing.service
    ```

6. Check the service status to ensure it is running:
    ```bash
    sudo systemctl status tuya_image_processing.service
    ```
## Mapping Media Folder in Home Assistant

To map a custom or additional media folder in Home Assistant, follow these steps:

1. Open your `configuration.yaml` file in your Home Assistant setup.
2. Add the following configuration under the `media_source` integration:

   ```yaml
   media_source:
     media_dirs:
       media: /path/to/your/media/folder
