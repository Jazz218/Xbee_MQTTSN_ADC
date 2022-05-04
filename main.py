# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import umqttsn.MQTTSNclient
import struct
import sys
import time
import xbee

from machine import ADC

class Callback:

    def published(self, MsgId):
        print("Published")

def connect_gateway():
    try:
        while True:
            try:
                aclient.connect()
                print('Connected to gateway...')
                break
            except:
                print('Failed to connect to gateway, reconnecting...')
                time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting...')
        sys.exit()

def register_topic():
    global topic1, topic2, topic3
    topic1 = aclient.register("topic1")
    print("topic1 registered.")
    topic2 = aclient.register("topic2")
    print("topic2 registered.")
    topic3 = aclient.register("topic3")
    print("topic3 registered.")

    aclient = umqttsn.MQTTSNclient.Client("client_sn_pub", "10.42.0.1", port=1883)
    aclient.registerCallback(Callback())
    connect_gateway()

    topic1 = None
    topic2 = None
    topic3 = None
    register_topic()

    payload1 = adc0.string
    payload2 = struct.pack('BBB', 3, 2, 1)
    payload3 = struct.pack('d', 3.14159265359)

    pub_msgid = aclient.publish(topic1, payload1, qos=0)
    time.sleep(1)
    pub_msgid = aclient.publish(topic2, payload2, qos=1)
    time.sleep(1)
    pub_msgid = aclient.publish(topic3, payload3, qos=2)
    time.sleep(1)

    aclient.disconnect()
    print("Disconnected from gateway.")

x = 0
adc0 = ADC("D0")

while(1):
    adc0_value = adc0.read() # pin 31
    adc0_string = str(adc0_value)

    print ("Attempt %d" % x)
    print("ADC0 value is: %d" % adc0_value)

    time.sleep(2)
    xbee.transmit(xbee.ADDR_BROADCAST, adc0_string)
    x = x+1

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
    # print("ADC1 value is: %d" % adc1_value)
    # print("ADC2 value is: %d" % adc2_value)
    # print("ADC3 value is: %d" % adc3_value)
    # adc1_value = adc1.read() # pin 30
    # adc2_value = adc2.read() # pin 29
    # adc3_value = adc3.read() # pin 28
    # adc1 = ADC("D1")
    # adc2 = ADC("D2")
    # adc3 = ADC("D3")