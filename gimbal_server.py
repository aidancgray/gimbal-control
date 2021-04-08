#!/usr/bin/python
# gimbal_server.py
# 2/15/21
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is a Python 2.7 script for controlling the gimbal
# system meant for the PFS project.
#
# EZHR17 Motor Controller for the monochromator loses memory
# after some time. Reinitialization must be done. This
# will be implemented as soon as I get around to it. The
# key settings are:
#  - /1f1R (flip home flag polarity)
#  - /1j4R (set to 1 microstep = 1/4 full step)
#
# -*- coding:utf-8 -*-

import serial
import time
import SocketServer
import pigpio
import sys


### Connect to a RS485 port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def connect(usbPort):
	# Creation of the serial connection
	t = serial.Serial(
                port = usbPort,
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
def manual(device, command):
        response = ''
        if device == 'stage':
  	        n = stageConn.write(command + '\r')
                time.sleep(0.1)
 	        out = stageConn.readline()
        else:
                n = monoConn.write(command + '\r')
                time.sleep(0.1)
 	        out = monoConn.readline()
        
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
                manual('stage', '/'+xstage.id+'A'+command[1]+'R')
                manual('stage', '/'+ystage.id+'A'+command[2]+'R')

                while waitFlag:
                        waitCheck1 = manual('stage', '/1Q')
                        waitCheck2 = manual('stage', '/2Q')

                        if waitCheck1[3] == '`' and waitCheck2[3] == '`':
                                waitFlag = False
                        else:
                                time.sleep(0.1)
        
        return response


### Monochromator Control Method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def MonoControl(wavelength):
        response = ''
        absPosition = int(round(wavelength * monoFit[0] + monoFit[1]))  # convert wavelength -> motor position
        response = manual('mono', '/1A' + str(absPosition) + 'R\r')  # send monochromator abs position 
        
        waitFlag = True
        while waitFlag:
                waitCheck = manual('mono','/1Q')

                if waitCheck[3] == '`':
                        waitFlag = False
                else:
                        time.sleep(0.1)

        return response


### Monochromator Command Parser ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def MonoParse(command):
        response = ''

        if len(command) >= 2 and command[1] != '?' and command[1] != 'home' and command[1][0] != '/':
                monoCommand = command[1]

                try:
                        wavelengthSet = float(monoCommand)

                        if wavelengthSet >= 0 and wavelengthSet <= 1750:
                                response = MonoControl(wavelengthSet)
                        else:
                                response = 'BAD\n' + response + 'wavelength range: 0-1750nm'

                except ValueError:
                        response = 'BAD\n' + response + 'command structure is: mono [wavelength in nm]'

        elif command[1] == '?':
                n = monoConn.write('/1?0' + '\r')  # query monochromator position 
                time.sleep(0.1)
                out = monoConn.readline()

                monoPosition = out.split('`')[1].split('\x03')[0]  # strip output
                wavelengthGet = round((float(monoPosition) - monoFit[1]) / monoFit[0], 2)  # convert to wavelength
                response = str(wavelengthGet) + '\n'

        elif command[1] == 'home':
                n = monoConn.write('/1Z40000V200P447V800R\r')
                time.sleep(0.1)
                out = monoConn.readline()
                
                waitFlag = True
                while waitFlag:
                        waitCheck = manual('mono','/1Q')

                        if waitCheck[3] == '`':
                                waitFlag = False
                        else:
                                time.sleep(0.1)
        
        elif command[1][0] == '/':
                response = manual('mono', command[1])

                waitFlag = True
                while waitFlag:
                        waitCheck = manual('mono','/1Q')

                        if waitCheck[3] == '`':
                                waitFlag = False
                        else:
                                time.sleep(0.1)

        else:
                response = 'BAD\n' + response + 'No wavelength specified'
        
        return response


### LED Control Method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def LEDControl(led, dutycycle):
        # If DC = 0, turn on all GPIO pins and set all to 0
        if int(dutycycle) == 0:
            for i in range(len(LEDList)):
                pi.set_mode(LEDList[i][1], pigpio.OUTPUT)  # set all pins to output mode
                pi.set_PWM_dutycycle(LEDList[i][1], 0)

            response = ''

        else:
            # Loop through list of LEDs to find which pin to use
            for i in range(len(LEDList)):
                pi.set_mode(LEDList[i][1], pigpio.INPUT)  # set all pins to input mode
                if led == LEDList[i][0]:
                    pin = LEDList[i][1]
                    LEDList[i][2] = dutycycle
                        
            response = ''
            pi.set_mode(pin, pigpio.OUTPUT)
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
                        
                        if len(command) >= 3:
                                dutycycle = command[2]

                                if (0 <= int(dutycycle)) and (int(dutycycle) <= 100):
                                        response = response
                                else:
                                        response = 'BAD\n' + response + 'Incorrect Dutycycle selection \n'
                        else:
                                dutycycle = '50'
                                
                        response = response + LEDControl(led, dutycycle)
                
        elif command[1] == '?':
                response = response + '-LED-|-Dutycycle-\n'

                for n in range(len(LEDList)):
                        # if len(LEDList[n][0]) == 3:
                        #         response = response + ' ' + LEDList[n][0] + ' | ' + str(int(float(pi.get_PWM_dutycycle(LEDList[n][1])) / 2.55)) + '%\n'
                        # else:
                        #         response = response + LEDList[n][0] + ' | ' + str(int(float(pi.get_PWM_dutycycle(LEDList[n][1])) / 2.55)) + '%\n'   
                        try:
                            response = response + LEDList[n][0] + ' | ' + str(int(float(pi.get_PWM_dutycycle(LEDList[n][1])) / 2.55)) + '%\n'
                        except:
                            response = response + LEDList[n][0] + ' | ' + '0' + '%\n'                 
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
                                response = manual('stage', command[0])
                        elif command[0] == 'move' and len(command) == 3:
                                response = moveStage(command)
                        elif command[0] == 'home' and command[1] == 'x':
                                response = xstage.homeStage(stageConn)
                        elif command[0] == 'home' and command[1] == 'y':
                                response = ystage.homeStage(stageConn)
                        elif command[0] == 'led' and len(command) >= 2:
                                response = LEDParse(command)
                        elif command[0] == 'mono' and len(command) >= 2:
                                response = MonoParse(command)
                        else:
                                # response = 'BAD\nStart motor commands with \'/\'. \
                                #         \nOr tell motor to move with \'move x y\' where x and y are real values. \
                                #         \nHome stage using \'home x/y\' and choose either x or y. \
                                #         \nControl the monochromator using \'mono wavelength\' where wavelength is in nm.'

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

        def homeStage(self, stageConn):
                response = "Homing the " + self.axis + " axis"
                waitFlag = True
                
                if self.id == '1':
                        stageConn.write(str.encode('/' + self.id + "v1000"+ "Z60000" + "V1000" + "A" + self.home + "R" + "\r"))
                        while waitFlag:
                                waitCheck1 = manual('stage', '/1Q')

                                if waitCheck1[3] == '`':
                                        waitFlag = False
                                else:
                                        time.sleep(0.1)
                                
                elif self.id == '2':
                        stageConn.write(str.encode('/' + self.id + "v500"+ "Z30000" + "V1000" + "A" + self.home + "R" + "\r"))
                        while waitFlag:
                                waitCheck2 = manual('stage', '/2Q')

                                if waitCheck2[3] == '`':
                                        waitFlag = False
                                else:
                                        time.sleep(0.1)
                        
                time.sleep(0.1)
                return response


if __name__ == "__main__":
        #stageConn = connect("/dev/ttyUSB0")
        monoConn = connect("/dev/ttyUSB1")
	pi = pigpio.pi()
        
        LEDs = ['635', '930', '970', '1050', '1070', '1085', '1200', '1300']
        LEDList = [['635', 23, 0],
                   ['930', 26, 0],
                   ['970', 13, 0],
                   ['1050', 6, 0],
                   ['1070', 5, 0],
                   ['1085', 22, 0],
                   ['1200', 27, 0],
                   ['1300', 17, 0]]
        
        LEDControl('635', 0)  # Set all LEDs to 0 at startup

        # (Controller Name, EZHR Address, Current Location, Center Location, Positive Limit, Lower Limit)
        xstage = Stage('X-Axis', '1', '0', '33000', '60000', '100')
        ystage = Stage('Y-Axis', '2', '0', '14000', '30000', '100')

        monoStepMode = 4.0  # 1/4 step mode for the monochromator
        monoFit = (4.003465 * monoStepMode, 109.8399 * monoStepMode)

        # Create the server, binding to the Pi's local IP  on port 9999
        HOST, PORT = "", 9999
        SocketServer.TCPServer.allow_reuse_address = True
        server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        try:
                server.serve_forever()
        except KeyboardInterrupt:
                print '...Closing server...'
                LEDControl('635', 0)  # Turn off all LEDs on shutdown
                server.shutdown()
                pi.stop()
        except:
                print 'Unknown Error'
