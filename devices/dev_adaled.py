#stroberry_pi device module for
# Adafruit LED Strip LPD8806

import RPi.GPIO as gpio 

__spidev = None

numarrays = 1
numleds = 8

#functions for device manipulation
#ALL device modules should implement these

def initialize_device():
    global __spidev
    __spidev = ("/dev/spidev0.0", "wb") 

def output_to_device(led_data):
    global __spidev, numarrays, numleds
    
    #confirm configuration is only one array and matches number of leds on device
    if len(led_data) != numarrays:
        print "Incorrect number of arrays for this device being handed in"
        return

    array = led_data[0]
    if len(array) != numleds:
        print "Incorrect number of LEDs for this device being handed in"
        return

    #convert RGB values into bytearrays
    #do we send RGB bytes or GRB bytes?
    #and do we gamma correct?

    #CHOOSE ONE:

    #create RGB bytearray with extra 0 bit on end for latch?
    #byte_data = bytearray(len(array) * 3 + 1)
    #for i, v in enumerate(array):
    #    bi = i *3
    #    byte_data[bi] = v[0]
    #    byte_data[bi + 1] = v[1]
    #    byte_data[bi + 2] = v[2]

    #create GRB bytearray with extra 0 bit on end for latch?
    #byte_data = bytearray(len(array) * 3 + 1)
    #for i, v in enumerate(array):
    #    bi = i *3
    #    byte_data[bi] = v[1]
    #    byte_data[bi + 1] = v[0]
    #    byte_data[bi + 2] = v[2]
    
    #create gamma converted GRB bytearray with extra 0 bit on end for latch?
    gamma = bytearray(256)
    for i in range(256):
       gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)
    byte_data = bytearray(len(array) * 3 + 1)
    for i, v in enumerate(array):
        bi = i *3
        byte_data[bi] = gamma[v[1]]
        byte_data[bi + 1] = gamma[v[0]]
        byte_data[bi + 2] = gamma[v[2]]
    
    __spidev.write(byte_data) 
    __spidev.flush() 

