#!/usr/bin/python
# -*- coding: UTF-8 -*-

import base64
import hashlib
import ssl
import websocket
import json
import time
import requests
import os
from dotenv import load_dotenv
import sys
import image_handler
import re

load_dotenv() 

try:
    import thread
except ImportError:
    import _thread as thread

# accessId, accessKey，serverUrl，MQ_ENV
ACCESS_ID           = os.getenv('ACCESS_ID')
ACCESS_KEY          = os.getenv('ACCESS_KEY')
API_ENDPOINT        = os.getenv('API_ENDPOINT')
DEVICE_ID           = os.getenv('DEVICE_ID')
WSS_SERVER_URL      = os.getenv('WSS_SERVER_URL')
MQ_ENV              = os.getenv('MQ_ENV')
JSON_PAYLOAD_VALUE  = os.getenv('JSON_PAYLOAD_VALUE')
JSON_PAYLOAD_KEY    = os.getenv('JSON_PAYLOAD_KEY')

# basic config
WEB_SOCKET_QUERY_PARAMS = "?ackTimeoutMillis=3000&subscriptionType=Failover"
SSL_OPT = {"cert_reqs": ssl.CERT_NONE}

CONNECT_TIMEOUT_SECONDS = 3
CHECK_INTERVAL_SECONDS = 3

PING_INTERVAL_SECONDS = 30
PING_TIMEOUT_SECONDS = 3

RECONNECT_MAX_TIMES = 1000

# global variable
global ws
ws = None

global reconnect_count
reconnect_count = 1

global connect_status
connect_status = 0


# topic env
def get_topic_url():
    return WSS_SERVER_URL + "ws/v2/consumer/persistent/" + ACCESS_ID + "/out/" + MQ_ENV + "/" + ACCESS_ID + "-sub" + WEB_SOCKET_QUERY_PARAMS


# handler message
def message_handler(payload):
    # print("payload:%s" % payload)
    dataMap = json.loads(payload)
    decryptContentDataStr = dataMap['data']
    pyCheck = format(decrypt_by_aes(decryptContentDataStr, ACCESS_KEY))
    print("\ndecryptContentData={}".format(pyCheck))


    regexMotion = re.compile(rf'{re.escape(JSON_PAYLOAD_VALUE)}') 
    if regexMotion.search(pyCheck):
        print('Motion triggered')
        print(pyCheck)
        data = unpack_data(pyCheck)
        image_handler.main(data)
        
    else:
        print('Data string found but no motion where triggered')

def unpack_data(data):
    json_string = re.sub(r'[^\x20-\x7E]+$', '', data)
    json_data = json.loads(json_string)
    value = json_data["status"][0].get(JSON_PAYLOAD_KEY)
    return value

# decrypt
def decrypt_by_aes(raw, key):
    import base64
    from Crypto.Cipher import AES
    raw = base64.b64decode(raw)
    key = key[8:24].encode("utf-8")
    cipher = AES.new(key, AES.MODE_ECB)
    raw = cipher.decrypt(raw)
    res_str = raw.decode('utf-8')
    res_str = eval(repr(res_str).replace('\\r', ''))
    res_str = eval(repr(res_str).replace('\\n', ''))
    res_str = eval(repr(res_str).replace('\\f', ''))
    return res_str


def md5_hex(md5_str):
    md = hashlib.md5()
    md.update(md5_str.encode('utf-8'))
    return md.hexdigest()


def gen_pwd():
    md5_hex_key = md5_hex(ACCESS_KEY)
    mix_str = ACCESS_ID+md5_hex_key
    return md5_hex(mix_str)[8:24]


def on_error(ws, error):
    print("on error is: %s" % error)


def reconnect():
    global reconnect_count
    print("ws-client connect status is not ok.\ntrying to reconnect for the %d time" % reconnect_count)
    reconnect_count += 1
    if reconnect_count < RECONNECT_MAX_TIMES:
        thread.start_new_thread(connect, ())


def on_message(ws, message):
    message_json = json.loads(message)
    payload = base64_decode_as_string(message_json["payload"])
    #print("---\nreceived message origin payload: %s" % payload)
    # handler payload
    try:
        message_handler(payload)
    except Exception as e:
        print("handler message, a business exception has occurred,e:%s" % e)
    send_ack(message_json["messageId"])


def on_close(obj):
    print("Connection closed!")
    obj.close()
    global connect_status
    connect_status = 0


def connect():
    print("ws-client started...")
    ws.run_forever(sslopt=SSL_OPT, ping_interval=PING_INTERVAL_SECONDS, ping_timeout=PING_TIMEOUT_SECONDS)


def send_ack(message_id):
    json_str = json.dumps({"messageId": message_id})
    ws.send(json_str)


def base64_decode_as_string(byte_string):
    byte_string = base64.b64decode(byte_string)
    return byte_string.decode('ascii')


def main():
    header = {"Connection": "Upgrade",
              "username": ACCESS_ID,
              "password": gen_pwd()}

    websocket.setdefaulttimeout(CONNECT_TIMEOUT_SECONDS)
    global ws
    ws = websocket.WebSocketApp(get_topic_url(),
                                header=header,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    thread.start_new_thread(connect, ())
    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        global reconnect_count
        global connect_status
        try:
            if ws.sock.status == 101:
                reconnect_count = 1
                connect_status = 1
        except Exception:
            connect_status = 0
            reconnect()


if __name__ == '__main__':
    main()