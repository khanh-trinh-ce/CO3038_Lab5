# Lecturer's code-------------------------------------------------------------------------------------------------------
import random

import numpy
import requests
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import simple_ai

# import geolocation

# Lecturer's code-------------------------------------------------------------------------------------------------------
print("Welcome to CO3038, Lab 3.")
BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "FGdNTjaigRJBidqrJZ60"

mess = ""
ser = ""
mask_res = ""

def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = -1
    # TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLED'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if temp_data['valueLED']:
                cmd = 1
            else:
                cmd = 0
        elif jsonobj['method'] == "setPump":
            temp_data['valuePump'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if temp_data['valuePump']:
                cmd = 3
            else:
                cmd = 2
    except:
        pass

    if getPort() != "None":
        ser.write((str(cmd) + "#").encode())


def connected(client, userdate, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection failed!")


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commport = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        #print(strPort)
        if "USB Serial Device" in strPort:
            splitPort = strPort.split(" ")
            commport = splitPort[0]
    return "/dev/cu.usbmodem14402"

# if getPort() != "None":
#     ser = serial.Serial(port=getPort(), baudrate=115200)


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[1] == "TEMP":
            _temp = {'temperature': splitData[2]}
            client.publish('v1/devices/me/telemetry', json.dumps(_temp), 1)
        elif splitData[1] == "LIGHT":
            _light = {'light': splitData[2]}
            client.publish('v1/devices/me/telemetry', json.dumps(_light), 1)
        elif splitData[1] == "HUMI":
            _humi = {'humidity': splitData[2]}
            client.publish('v1/devices/me/telemetry', json.dumps(_humi), 1)

    except:
        pass
#
def ai_check():
    simple_ai.capture_image()

    res = simple_ai.ai_detection()
    print(res)
    return res

def readSerial():
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if end == len(mess):
                mess = ""
            else:
                mess = mess[end + 1:]


# Lecturer's code-------------------------------------------------------------------------------------------------------
client = mqttclient.Client("Gateway_Thingsboard")

client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message
# ----------------------------------------------------------------------------------------------------------------------

counter = 0
# -----------------------------------------------------------------------------------------------------------------------
while True:
    # if getPort() != "None":
    # readSerial()
    mask_res = ai_check()
    # Get coordinates using WinRT-based functions.
    # latitude = geolocation.get_location()[0]
    # longitude = geolocation.get_location()[1]

    # Get city name from coordinates using GeoPy.
    # where = geolocation.geolocator.reverse(str(latitude) + "," + str(longitude))
    # address = where.raw['address']
    # city = address.get('city', '')
    # state = address.get('state', '')
    # country = address.get('country', '')
    # humidity = address.get('humidity', '')

    # Using OpenWeather API to get dynamic temperature and humidity.
    # complete_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={geolocation.api_key}"
    # response = requests.get(complete_url)
    # response_json = response.json()

    # if response_json["cod"] != "404":
    #     response_json_main = response_json["main"]
    #     # Convert from Kelvin to Celsius.
    #     temp = response_json_main["temp"]-273.15
    #
    # humi = response_json_main["humidity"]

    # Convert data to JSON.
    # collect_data = {'longitude': longitude,
    #                 'latitude': latitude, 'city': city, 'state': state, 'country': country, 'humidity': humi}

    # Changes light intensity and loops back if overflow.
    # light_intensity += 1
    # if (light_intensity > 100):
    #     light_intensity = 0

    # Send data to server.
    # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    # Print to console to check.
    # print("Current location: ", city, ", ", state, ", ", country)
    counter = counter - 1
    if counter <= 0:
        _light = {'light': random.randint(0, 300)}
        client.publish('v1/devices/me/telemetry', json.dumps(_light), 1)
        _humidity = {'humidity': random.randint(0, 100)}
        client.publish('v1/devices/me/telemetry', json.dumps(_humidity), 1)
        # if mask_res[0] == 0:
        #     _mask = {'mask': 'Masked'}
        # elif mask_res[0] == 1:
        #     _mask = {'mask': 'Unmasked'}
        # elif mask_res[0] == 2:
        #     _mask = {'mask': 'No one'}
        _mask = {'mask' : mask_res[0]}
        client.publish('v1/devices/me/telemetry', json.dumps(_mask), 1)
        _perc = {'percentage' : float(mask_res[1] * 100)}
        client.publish('v1/devices/me/telemetry', json.dumps(_perc), 1)
        counter = 5
    time.sleep(1)
