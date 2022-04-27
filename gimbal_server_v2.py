#!/usr/bin/python
# gimbal_server_v2.py
# 4/27/21
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is a Python 2.7 script for controlling the gimbal
# system meant for the PFS project.
#
# EZHR17 Motor Controller for the monochromator loses memory
# after some time. Reinitialization must be done. The
# key settings are:
#  - /1f1R (flip home flag polarity)
#  - /1j4R (set to 1 microstep = 1/4 full step)
#
# EZHR23 - Y Stage:
#  - /2V500R (set velocity)
#  - /2m70R
#
# EZHR23 - X Stage:
#  - 
# -*- coding:utf-8 -*-

import serial
import time
import SocketServer
import pigpio
import sys

from deviceClass import Device
from stageClass import Stage
from monoClass import Mono
from ledClass import LED

X_MICROSTEP = 32
Y_MICROSTEP = 64

# Method for moving the 2 stages in parallel
def multiStageMove(xMove, yMove):
        responseX = xstage.moveStage_NB(xMove)
        responseY = ystage.moveStage_NB(yMove)

        waitFlag = True
        while waitFlag:
                waitCheck1 = xstage.manual('/1Q')
                waitCheck2 = ystage.manual('/2Q')

                if waitCheck1[3] == '`' and waitCheck2[3] == '`':
                        waitFlag = False
                else:
                        time.sleep(0.1)

        response = responseX + responseY
        response = response.replace('\n',';')
        return response

# Method for getting both stage statuses
def multiStageStatus():
        responseX = xstage.status()
        responseY = ystage.status()
        response = responseX + ';' + responseY + ';'
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
                                response = stageConn.manual('stage', command[0])
                        elif command[0] == 'move' and len(command) == 3:
                                response = multiStageMove(command[1], command[2])
                        elif command[0] == 'home' and command[1] == 'x':
                                response = xstage.homeStage(stageConn)
                        elif command[0] == 'home' and command[1] == 'y':
                                response = ystage.homeStage(stageConn)
                        elif command[0] == 'stages' and command[1] == '?':
                                response = multiStageStatus()
                        elif command[0] == 'led' and len(command) >= 2:
                                response = LEDobj.LEDParse(command)
                        elif command[0] == 'mono' and len(command) >= 2:
                                response = monochromator.MonoParse(command)
                        else:
                                response = 'BAD\n'
                                
                if response[0:3] != 'BAD':
                        response = response + 'OK\n'
                
                self.wfile.write(response)

if __name__ == "__main__":
        stageConn = Device("/dev/ttyUSB0")
        monoConn = Device("/dev/ttyUSB1")
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
        
        LEDobj = LED(pi, LEDs, LEDList)  # Create LED object

        LEDobj.LEDControl('635', 0)  # Set all LEDs to 0 at startup

        # (Controller Name, EZHR Address, Current Location, Center Location, Positive Limit, Lower Limit)
        xstage = Stage('X', '1', X_MICROSTEP, '0', 66000, 120002, 198, stageConn)
        ystage = Stage('Y', '2', Y_MICROSTEP, '0', 28000, 58002, 198, stageConn)

        ystage.manual('/2m70R')  # Set the move-current to 70%.

        monochromator = Mono(pi, 20, monoConn, 4.0) # Create monochromator object

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
                LEDobj.LEDControl('635', 0)  # Turn off all LEDs on shutdown
                monochromator.MonoPower(0)  # Turn off Lamp to Monochromator
                server.shutdown()
                pi.stop()
        except:
                print 'Unknown Error'
