#timelord python code - based on various sources, code snippets from AlexEames
# @raspi.tv
# time logic elements from Tim Clark's clock-off.py @ github.com/tcsoft/clock-off
# Pimoroni Four Char sample code
#
# dependencies:
# 1. sudo pip install paho-mqtt
# 2. Pimoroni Four Letter phat drivers https://github.com/pimoroni/fourletter-phat
# not yet created 'as a service' so folder structure not yet bottomed out,
# nor installation code
# configuration file for mqtt listener 'included' at run time
#
# needs the byte code conversion fix - seen during testing, but only triggered when
# upgrading the build on the officeclock target system :(


import sys
sys.path.insert(0, "/home/pi/mozzy")

#from mozzy folder
import mosquittosettings
#from same folder as timelord
import timelordsettings
import time
import argparse
import subprocess
import paho.mqtt.client as mqtt
import fourletterphat as flp

from datetime import datetime
from datetime import date

#setup globals
debug = False
fourchar_payload = "99999"
fourchar_blank = "    "
fourchar_flag = False

#setup mqtt handlers

def on_connect(mqttc, obj, flags, rc):
    global debug
    if debug == True:
        print("ON_connect run, Connected to %s:%s" % (mqttc._host, mqttc._port))

def on_message(mqttc, obj, msg):
    global debug
    global fourchar_blank
    global fourchar_payload
    global fourchar_flag
    if debug == True:
        print("on_message handler fired")
        print('handler values',msg.topic+" "+str(msg.qos)+" "+str(msg.payload, encoding='utf8'))
        print('value sent',str(msg.payload, encoding='utf-8'))
# needs protection logic here to REJECT non numeric feeds, also cannot handle
# json strings
    fourchar_payload = str(msg.payload, encoding='utf8')
    fourchar_flag = True
    

def on_publish(mqttc, obj, mid):
    global debug
    if debug == True:
        print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    global debug
    if debug == True:
        print("Subscribed: to "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    global debug
    if debug == True:
        print('on_log event',string)

# showtime is the main code logic loop, handling the time AND displaying the
# temperature received on the MQTT pub sub q

def showtime():
    global debug
    global fourchar_flag
    global fourchar_payload

# old logic actually worked, to a point
    fourchar_flag = False
    str_time = time.strftime("%H%M")
    flp.print_number_str(str_time)
    if int(time.time()) % 2 == 0:
        flp.set_decimal(1, 1)
    else:
        flp.set_decimal(1, 0)
    flp.show()
    time.sleep(0.1)
# new logic
#    flp.print_str("    ")
#    flp.show
#    float_temp = float(fourchar_payload)
#    flp.print_float(float_temp, decimal_digits=1, justify_right=True)
#    flp.show()
#    time.sleep(2)
    
# old logic
    if fourchar_flag == True:
        flp.print_str("    ")
        flp.show
        float_temp = float(fourchar_payload)
        flp.print_float(float_temp, decimal_digits=1, justify_right=True)
        flp.show()
        time.sleep(2)


bright_time = datetime.strptime(timelordsettings.bright_time, "%H:%M")
dim_time = datetime.strptime(timelordsettings.dim_time, "%H:%M")
now_time = time.strftime("%H:%M")
now_time = datetime.strptime(now_time, "%H:%M")

def isNowInTimePeriod(bright_time, dim_time, now_time):
    if bright_time < dim_time:
       return now_time >= bright_time and now_time <= dim_time
    else: #Over midnight
       return now_time >= bright_time or  now_time <= dim_time


apex_mqtt_broker = mosquittosettings.apex_mqtt_broker
apex_mqtt_port = mosquittosettings.mqtt_port
apex_clock_channel = mosquittosettings.mqtt_clock_channel


# ******************************  END SETUP ******************************

# code start

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(apex_mqtt_broker, apex_mqtt_port, 60)
client.loop_start()
client.subscribe(apex_clock_channel)

# Instantiate the parser
parser = argparse.ArgumentParser(description='set debug flag?')


# optional argument - debug
parser.add_argument("debug_code", type=str, nargs='?',
                    help='Send a D or d to debug code')

args = parser.parse_args()


debug_flag = (args.debug_code)
if debug_flag in ['D','d']:
    debug = True
    print("Argument values",debug_flag)


def main():

    while True:
        showtime()
        now_time = time.strftime("%H:%M")
        now_time = datetime.strptime(now_time, "%H:%M")
        if isNowInTimePeriod(bright_time, dim_time, now_time) == True:
            flp.set_brightness(timelordsettings.display_bright)
        else:
            flp.set_brightness(timelordsettings.display_dim)
        if debug == True:
            print('Listening for message on',apex_clock_channel)
            time.sleep(5)

if __name__ == '__main__':
    main()
