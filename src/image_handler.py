#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tuya_connector import TuyaOpenAPI
import base64
import sys
import json
from urllib.request import urlopen
from Crypto.Cipher import AES
import struct
import io, os, datetime
from dotenv import load_dotenv
import hass_webhook

load_dotenv() 
BLOCK_SIZE          = 16
ACCESS_ID           =  os.getenv('ACCESS_ID')
ACCESS_KEY          =  os.getenv('ACCESS_KEY')
API_ENDPOINT        =  os.getenv('API_ENDPOINT')
DEVICE_ID           =  os.getenv('DEVICE_ID')
FILE_PATH           =  os.getenv('FILE_PATH')
HASS_URL            = os.getenv('HASS_URL')
HASS_MESSAGE        = os.getenv('HASS_MESSAGE')
HASS_WEBHOOK_NAME   = os.getenv('HASS_WEBHOOK_NAME')
HASS_WWW_FILE       = os.getenv('HASS_WWW_FILE')


def pad(byte_array:bytearray):
        pad_len = BLOCK_SIZE - len(byte_array) % BLOCK_SIZE
        return byte_array + (bytes([pad_len]) * pad_len)
    
def unpad(s:bytearray):
    return s[:-ord(s[len(s)-1:])]

def add_trailing_slash(path):
    if not path.endswith('/'):
        return path + '/'
    return path

def main(data: str):

    fileName = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpeg"
    imagePath = add_trailing_slash(FILE_PATH) + fileName 

    # Init OpenAPI and connect
    openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
    openapi.connect()

    base64String = data
    decoded = json.loads(base64.b64decode(base64String))
    bucket = decoded["bucket"]
    file = decoded["files"][0][0]
    key = decoded["files"][0][1].encode('utf-8')

    fileURLFetch = openapi.get("/v1.0/devices/{0}/movement-configs?bucket={1}&file_path={2}".format(DEVICE_ID, bucket, file))
    print(fileURLFetch)
    actualFileURL = fileURLFetch["result"]
    fileContents = urlopen(actualFileURL).read()

    with io.BytesIO(fileContents) as src_file:
        # seems to be 1, which 
        version = struct.unpack('i', src_file.read(4))[0]
        iv = src_file.read(16)
        src_file.read(44)
        
        file_contents = src_file.read()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        result = cipher.decrypt(pad(file_contents))

        with open(imagePath, "wb") as binary_file:
            binary_file.write(result)

    hass_webhook.send_to_webhook(HASS_MESSAGE,
                                HASS_URL, 
                                HASS_WWW_FILE,
                                HASS_WEBHOOK_NAME,
                                fileName)

if __name__ == '__main__':
    main()