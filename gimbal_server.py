#!/usr/bin/python
# gimbal_server.py
# 3/3/20
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is a Python 2.7 script for controlling the gimbal
# system meant for the PFS project.
#
# -*- coding:utf-8 -*-

import serial, time, pigpio, SocketServer, sys

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
		print t.portstr + ' is open...'
                return t
        
### Manual Control ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def manual(command):
        response = ''
  	n = t.write(command + '\r')
        time.sleep(0.1)
 	out = t.readline()
        if command[2] == 'Q':
                response = out[:len(out)-3] + '\n'
 	else:
                response = out[4:len(out)-3] + '\n'
        return response

### Move Stage Control ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def moveStage(command):
        response = ''
        xFlag = True
        yFlag = True
        waitFlag = True
        
        if (int(command[1]) >= int(xstage.pos)) or (int(command[1]) <= int(xstage.neg)):
                xFlag = False 
                response = 'BAD\n' + response + 'X Position out of range\n'
        
        if (int(command[2]) >= int(ystage.pos)) or (int(command[2]) <= int(ystage.neg)):
                yFlag = False
                response = 'BAD\n' + response + 'Y Position out of range'
                
        if xFlag and yFlag:
                manual('/'+xstage.id+'A'+command[1]+'R')
                manual('/'+ystage.id+'A'+command[2]+'R')

                while waitFlag:
                        waitCheck1 = manual('/1Q')
                        waitCheck2 = manual('/2Q')

                        if waitCheck1[3] == '`' and waitCheck2[3] == '`':
                                waitFlag = False
                        else:
                                time.sleep(0.1)
        
        return response
                
### LED Control Method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def LEDControl(led, dutycycle):
        pi = pigpio.pi()

        # Loop through list of LEDs to find which pin to use
        for i in range(len(LEDList)):
                if led == LEDList[i][0]:
                        pin = LEDList[i][1]
                        LEDList[i][2] = dutycycle
                        
        #response = 'Setting '+ led + ' to ' + str(dutycycle) + '%'
        response = ''
        pi.set_PWM_dutycycle(pin, 255 * (float(dutycycle)/100))
        return response

### LED Command Parser ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def LEDParse(command):
        response = ''
        
        if len(command) >= 2 and command[1] != '?':
                led = command[1]

                if led not in LEDs:
                        response = 'BAD\n' + response + 'Incorrect LED selection \n'
                else:
                        #response = response + 'LED: ' + led + 'nm\n'
                        
                        if len(command) >= 3:
                                dutycycle = command[2]

                                if (0 <= int(dutycycle)) and (int(dutycycle) <= 100):
                                        response = response
                                else:
                                        response = 'BAD\n' + response + 'Incorrect Dutycycle selection \n'
                        else:
                                #response = response + 'Dutycycle: 50% (default) \n'
                                dutycycle = '50'
                                

                        response = response + LEDControl(led, dutycycle)
                
        elif command[1] == '?':
                response = response + '-LED-|-Dutycycle-\n'

                for n in range(len(LEDList)):
                        if len(LEDList[n][0]) == 3:
                                response = response + ' ' + LEDList[n][0] + ' | ' + str(LEDList[n][2]) + '%\n'
                        else:
                                response = response + LEDList[n][0] + ' | ' + str(LEDList[n][2]) + '%\n'
                        
        else:
                response = 'BAD\n' + response + 'No LED specified'
        
        return response

### TCP Server Class ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MyTCPHandler(SocketServer.StreamRequestHandler):

        def handle(self):
                # self.rfile is a file-like object created by the handler;
                # we can now use e.g. readline() instead of raw recv() calls
                self.data = self.rfile.readline().strip()

                if self.data == '' or self.data == ' ':
                        response = 'No arguments/commands supplied.'
                else:
                        command = self.data.split()
                
                        if command[0][0] == '/':
                                response = manual(command[0])
                        elif command[0] == 'move' and len(command) == 3:
                                response = moveStage(command)
                        elif command[0] == 'home' and command[1] == 'x':
                                response = xstage.homeStage(t)
                        elif command[0] == 'home' and command[1] == 'y':
                                response = ystage.homeStage(t)
                        elif command[0] == 'led' and len(command) >= 2:
                                response = LEDParse(command)
                        else:
                                #response = 'BAD\nStart motor commands with \'/\'. \nOr tell motor to move with \'move x y\' where x and y are real values. \nHome stage using \'home x/y\' and choose either x or y. \nControl the LEDs using \'led wavelength dutycycle\' where wavelength and dutycycle are real values.'
                                response = 'BAD\n'
                                
                if response[0:3] != 'BAD':
                        response = response + 'OK\n'
                
                # Likewise, self.wfile is a file-like object used to write back
                # to the client
                self.wfile.write(response)
                                
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

        def homeStage(self, t):
                response = "Homing the " + self.axis + " axis"
                waitFlag = True
                
                if self.id == '1':
                        t.write(str.encode('/' + self.id + "v1000"+ "Z60000" + "V1000" + "A" + self.home + "R" + "\r"))
                        while waitFlag:
                                waitCheck1 = manual('/1Q')

                                if waitCheck1[3] == '`':
                                        waitFlag = False
                                else:
                                        time.sleep(0.1)
                                
                elif self.id == '2':
                        t.write(str.encode('/' + self.id + "v500"+ "Z30000" + "V1000" + "A" + self.home + "R" + "\r"))
                        while waitFlag:
                                waitCheck2 = manual('/2Q')

                                if waitCheck2[3] == '`':
                                        waitFlag = False
                                else:
                                        time.sleep(0.1)
                        
                time.sleep(0.1)
                
                return response
                
### Main function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
        t = connect()

        LEDs = ['635', '930', '970', '1050', '1070', '1085', '1200', '1300']
        LEDList = [['635', 23, 0],
                   ['930', 26, 0],
                   ['970', 13, 0],
                   ['1050', 6, 0],
                   ['1070', 5, 0],
                   ['1085', 22, 0],
                   ['1200', 27, 0],
                   ['1300', 17, 0]]
	
        # (Controller Name, EZHR Address, Current Location, Center Location, Positive Limit, Lower Limit)
        xstage = Stage('X-Axis', '1', '0', '33000', '60000', '100')
        ystage = Stage('Y-Axis', '2', '0', '14000', '30000', '100')

        # Create the server, binding to the Pi's local IP  on port 9999
        HOST, PORT = "192.168.1.198", 9999
        SocketServer.TCPServer.allow_reuse_address = True
        server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        try:
                server.serve_forever()
        except KeyboardInterrupt:
                print '...Closing server...'
                server.shutdown()
        except:
                print 'Unknown Error'
