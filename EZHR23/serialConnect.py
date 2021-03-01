#!/usr/bin/python
import serial
import time

loop = True

ezhr = serial.Serial(
    port = '/dev/ttyS0',
    baudrate = 115200,
    stopbits = serial.STOPBITS_ONE,
    parity = serial.PARITY_NONE
)

while loop:
    strInput = input('Enter command: ')
    if (strInput == 'q'):
        loop = False
    n = ezhr.write(str.encode(strInput))
    str = ser.readall()    

