import time

### Stage class ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### axis: name of the stage (x, y, etc.)
### id: the address for the EZHR23 Controller
### loc: the current position of the stage (home, pos, neg)
### home: the "center" of the stage, or where it positions the collimator on-axis
### pos: the location of the positive position
### neg: the location of the negative position
### devConn: holds the connection to the motor controller(s)
class Stage:
        def __init__(self, axis, id, microstepMode, moveCurrent, holdCurrent, startVelocity, maxVelocity, home, posLimit, negLimit, devConn):
                self.axis = axis
                self.id = id
                self.microstepMode = microstepMode
                self.moveCurrent = moveCurrent
                self.holdCurrent = holdCurrent

                if startVelocity > 2500:
                        self.startVelocity = 2500
                elif startVelocity < 200:
                        self.startVelocity = 200
                else:
                        self.startVelocity = startVelocity

                if maxVelocity > 10000:
                        self.maxVelocity = 10000
                elif maxVelocity < 50:
                        self.maxVelocity = 50
                else:                
                        self.maxVelocity = maxVelocity 
                
                self.startVelocity_MS = 0
                self.maxVelocity_MS = 0
                
                self.home = home * 2
                self.pos = posLimit
                self.neg = negLimit
                self.devConn = devConn

                self.manual('/' + self.id + 'm' + str(self.moveCurrent) + 'R')
                self.manual('/' + self.id + 'h' + str(self.holdCurrent) + 'R')

                self.changeMicrostepMode(self.microstepMode)

        def changeMicrostepMode(self, microstepMode):
                try:
                        msMode = int(microstepMode)
                except:
                        return 'BAD; Microstep Mode must be 2, 4, 8, 16, 32, 64, 128, or 256;'
                
                if msMode == 2 or msMode == 4 or msMode == 8 or msMode == 16 or msMode == 32 or msMode == 64 or msMode == 128 or msMode == 256:
                        self.microstepMode = msMode
                        
                        if self.startVelocity * self.microstepMode > 2500:
                                self.startVelocity_MS = 2500
                        elif self.startVelocity * self.microstepMode < 200:
                                self.startVelocity_MS = 200
                        else:
                                self.startVelocity_MS = self.startVelocity * self.microstepMode
                        
                        if self.maxVelocity * self.microstepMode > 10000:
                                self.maxVelocity_MS = 10000
                        elif self.maxVelocity * self.microstepMode < 50:
                                self.maxVelocity_MS = 50
                        else:                
                                self.maxVelocity_MS = self.maxVelocity * self.microstepMode

                        self.pos_MS = self.pos * self.microstepMode
                        self.neg_MS = self.neg * self.microstepMode

                        self.manual('/' + self.id + 'j' + str(self.microstepMode) + 'R')
                        self.manual('/' + self.id + 'v' + str(self.startVelocity_MS) + 'R')
                        self.manual('/' + self.id + 'V' + str(self.maxVelocity_MS) + 'R')

                        return ''
                else:
                        return 'BAD; Microstep Mode must be 2, 4, 8, 16, 32, 64, 128, or 256;'

        def homeStage(self):
                response = "Homing the " + self.axis + " axis;"
                waitFlag = True
                homeSpeed = str(self.maxVelocity * 2)
                homeLimit = str(self.pos * 2)
                
                self.manual('/' + self.id + 'j2' + 'R')
                self.manual('/' + self.id + 'v' + homeSpeed + 'R')
                self.manual('/' + self.id + 'Z' + homeLimit + 'V' + homeSpeed + 'A' + str(self.home) + 'R')
                time.sleep(0.1)
                
                while waitFlag:
                        waitCheck1 = self.manual('/' + self.id + 'Q')

                        if waitCheck1[3] == '`':
                                waitFlag = False
                                time.sleep(0.1)
                        else:
                                time.sleep(0.1)
                
                self.manual('/' + self.id + 'j' + str(self.microstepMode) + 'R')
                self.manual('/' + self.id + 'v' + str(self.startVelocity_MS) + 'R')
                self.manual('/' + self.id + 'V' + str(self.maxVelocity_MS) + 'R')
                
                return response

        def moveStage(self, position):
                response = ''
                waitFlag = True
                
                if (int(position) >= int(self.pos_MS)) or (int(position) <= int(self.neg_MS)):
                        response = 'BAD;' + response + 'Position out of range;'
                        
                else:
                        self.manual('/'+self.id+'A'+str(position)+'R')

                        while waitFlag:
                                waitCheck = self.manual('/'+self.id+'Q')

                                if waitCheck[3] == '`':
                                        waitFlag = False
                                else:
                                        time.sleep(0.1)
                
                return response
        
        # A version of the moveStage command that's non-blocking, for moving multiple stages in parallel
        def moveStage_NB(self, position):
                response = ''
                
                if (int(position) >= int(self.pos_MS)) or (int(position) <= int(self.neg_MS)):
                        response = 'BAD;' + response + 'Position out of range;'
                        
                else:
                        self.manual('/'+self.id+'A'+str(position)+'R')
                
                return response

        def manual(self, command):
                response = ''

                self.devConn.write(command + '\r')
                time.sleep(0.1)
                out = self.devConn.readline()
                
                if command[2] == 'Q':
                        response = out[:len(out)-3]
                else:
                        response = out[4:len(out)-3]
                
                return response
        
        def status(self):
                response = self.axis + '=' + self.manual('/'+self.id+'?8')
                return response