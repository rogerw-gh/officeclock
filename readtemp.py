# fixing the byte code problem - but its not in here..
#
# generic file read / write test code
import os
import sys
sys.path.insert(0, "/home/pi/mozzy")
import paho.mqtt.client as mqtt
import mosquittosettings
import argparse
import readtempsettings
import platform
import time

# ************************** setup pre-reqs   
running_hostname = platform.node()
live_hostname = checkfilesettings.host_name
#Mosquitto setup
apex_mqtt_broker = mosquittosettings.apex_mqtt_broker
apex_mqtt_port = mosquittosettings.mqtt_port
apex_clock_channel = mosquittosettings.mqtt_clock_channel
mozzy_channel = apex_clock_channel
update_wait_time = checkfilesettings.update_wait_time

# setup interrupts

def on_connect(mqttc, obj, flags, rc):
    global debug
    if debug ==True:
        print("ON_connect run, Connected to %s:%s" % (mqttc._host, mqttc._port))


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


def do_message(message):
    # write log message
#    print("Log file ",message)
    # write mosquitto message
    print("Mosquitto message",message)

#***************   END SETUP ***************





debug = False

def main():
    global debug
    
# Instantiate the parser
    parser = argparse.ArgumentParser(description='Check debug flag')

# optional argument - debug
    parser.add_argument("debug_code", type=str, nargs='?',
                        help='Send a D or d to debug code')

    args = parser.parse_args()

    debug_flag = (args.debug_code)
    if debug_flag in ['D','d']:
        debug = True
        print("Argument values",debug_flag)

    if running_hostname == live_hostname:
        data_file = checkfilesettings.file_name
    else:
        data_file = checkfilesettings.test_file
    if debug: print(data_file)
    
    try:
        with open(data_file) as file:
            if debug: print('here')
            pass
    except IOError as e:
        print ('Unable to open file ', data_file) #Does not exist OR no read permissions
        if debug: print('This is bad, the', data_file, 'file doesn\'t exist')
        sys.exit('The data file doesn\'t exist or no read permissions')

#   so now the main body of the code which needs a code block indent

    while True:
        global update_wait_time
        file_handle = open(data_file, mode='r')
        file_text = file_handle.readlines()
        file_handle.close()

        if debug: print ('contents of file',file_text)
        temp_str = file_text[1]

        if debug: print ('contents of second list object',temp_str)

        temp_str = temp_str.split('=')
        if debug: print ('contents of temperature value',temp_str[1])

        # now do some conversions
        temp_num = float(temp_str[1])/1000
        if debug: print ('temperature div 1000 = ',temp_num)
       
        mozzy_message = (temp_num)

        if debug == True:
           print (mozzy_channel,mozzy_message)

        client = mqtt.Client("Send_stream")
        client.on_publish = on_publish
        client.on_connect = on_connect

        client.connect(apex_mqtt_broker, apex_mqtt_port, 60)
        ret = client.publish(mozzy_channel,mozzy_message)
       # now wait for a bit before repeating the block

        time.sleep(update_wait_time)



# end of main code block

if __name__ == '__main__':
    main()
