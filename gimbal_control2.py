#!/usr/bin/python
# Gimbal_Control.py
# 8/22/18
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is a Python 3.5 script for controlling the gimbal
# system meant for the PFS project.
#
# -*- coding:utf-8 -*-

import serial, time

### Connect to the RS485 port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def connect():
    # Creation of the serial connection
    t = serial.Serial(
            port = '/dev/ttyUSB0',
            baudrate = 9600,
            timeout = 1,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            xonxoff = False
    )
    
    t.close()
    t.open()
    
    # Confirm the connection is open
    if t.isOpen():
        print(t.portstr + ' is open...')
        return t

### Manual Control ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def manual(t):
    flag = True
    print('Enter command or B to return to main menu')
    while flag:
        strInput = input('$ ')

        if strInput.upper() == 'B':
            flag = False
        else:
            n = t.write(str.encode(strInput + '\r')) # THIS ONE WORKS
            print('Bytes written:' + str(n))
            out = t.readline()
            #out = bytearray.fromhex(out).decode()
            #print('Receiving...')	

### Choice control ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def choice(t, xstage, ystage):
    flag = True
    while flag:
        print('')
        print('[1]  [2]  [3]')
        print('[4]  [5]  [6]')
        print('[7]  [8]  [9]')
        strInput = input('Choose position or B to return to main menu: ')
	
        if '1' in strInput.upper():
            xstage.move(t, -1)
            ystage.move(t, 1)
	                
        elif '2' in strInput.upper():
            xstage.move(t, 0)
            ystage.move(t, 1)
	                                
        elif '3' in strInput.upper():
            xstage.move(t, 1)
            ystage.move(t, 1)
                                
        elif '4' in strInput.upper():
            xstage.move(t, -1)
            ystage.move(t, 0)
                                
        elif '5' in strInput.upper():
            xstage.move(t, 0)
            ystage.move(t, 0)
                                
        elif '6' in strInput.upper():
            xstage.move(t, 1)
            ystage.move(t, 0)
                                
        elif '7' in strInput.upper():
            xstage.move(t, -1)
            ystage.move(t, -1)
                                
        elif '8' in strInput.upper():
            xstage.move(t, 0)
            ystage.move(t, -1)
                                
        elif '9' in strInput.upper():
            xstage.move(t, 1)
            ystage.move(t, -1)
                                
        elif strInput.upper() == 'B':
            flag = False
        
        else:
            print('ERROR: Please choose a # 1-9')

        n = t.write(str.encode('/AR\r'))

### Stage class ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### axis: name of the stage (x, y, etc.)
### id: the address for the EZHR23 Controller
### loc: the current position of the stage (home, pos, neg)
### home: the "center" of the stage, or where it positions the collimator on-axis
### pos: the location of the positive position
### neg: the location of the negative position
class Stage:
    def __init__(self, axis, id, loc, home, pos, neg):
        self.axis = axis
        self.id = id
        self.loc = loc
        self.home = home
        self.pos = pos
        self.neg = neg

    def move(self, t, position):
        if self.loc == position:
            print(self.axis + ': holding position')

        elif position == 0:
            print(self.axis + ': moving to center')
            t.write(str.encode('/' + self.id + 'A' + self.home + '\r'))
            self.loc = 0
                
        elif position == 1:
            print(self.axis + ': moving to +')
            t.write(str.encode('/' + self.id + 'A' + self.pos + '\r'))
            self.loc = 1
                
        elif position == -1:
            print(self.axis + ': moving to -')
            t.write(str.encode('/' + self.id + 'A' + self.neg + '\r'))
            self.loc = -1
        time.sleep(0.1)

### Main function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    t = connect()
                    
              # (Controller Name, EZHR Address, Current Location, Home Location, Positive Location, Negative Location)		  
    xstage = Stage('X-Axis', '1', '0', '2500', '0', '5000')
    ystage = Stage('Y-Axis', '2', '0', '2500', '0', '5000')
    
    # Accept commands until user chooses to quit
    while True:
        menuInput = input('Enter M for manual control, C for choice menu, or Q to exit: ')

        if 'M' == menuInput.upper():
            manual(t)

        elif 'C' == menuInput.upper():
            choice(t, xstage, ystage)	      
                        
        elif menuInput.upper() == 'Q':
            t.close()
            exit()

        else:
            print('ERROR: Please choose M/C/Q')

if __name__ == "__main__":
	main()
