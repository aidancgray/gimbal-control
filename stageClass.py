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
                self.startVelocity = startVelocity * self.microstepMode
                self.maxVelocity = maxVelocity * self.microstepMode
                self.home = home * self.microstepMode
                self.pos = posLimit * self.microstepMode
                self.neg = negLimit * self.microstepMode
                self.devConn = devConn

                self.manual('/' + self.id + 'j' + self.microstepMode + 'R')
                self.manual('/' + self.id + 'm' + self.moveCurrent + 'R')
                self.manual('/' + self.id + 'h' + self.holdCurrent + 'R')
                self.manual('/' + self.id + 'v' + self.startVelocity + 'R')
                self.manual('/' + self.id + 'V' + self.maxVelocity + 'R')

        def homeStage(self, stageConn):
                response = "Homing the " + self.axis + " axis"
                waitFlag = True

                self.devConn.write(str.encode('/' + self.id + 'v' + self.maxVelocity + 'Z' + self.pos + 'V' + self.maxVelocity + "A" + self.home + "R" + "\r"))
                while waitFlag:
                        waitCheck1 = self.manual('/' + self.id + 'Q')

                        if waitCheck1[3] == '`':
                                waitFlag = False
                        else:
                                time.sleep(0.1)
                time.sleep(0.1)
                return response

        def moveStage(self, position):
                response = ''
                waitFlag = True
                
                if (int(position) >= int(self.pos)) or (int(position) <= int(self.neg)):
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
                
                if (int(position) >= int(self.pos)) or (int(position) <= int(self.neg)):
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