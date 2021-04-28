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
        def __init__(self, axis, id, loc, home, pos, neg, devConn):
                self.axis = axis
                self.id = id
                self.loc = loc
                self.home = home
                self.pos = pos
                self.neg = neg
                self.devConn = devConn

        def homeStage(self, stageConn):
                response = "Homing the " + self.axis + " axis"
                waitFlag = True
                
                if self.id == '1':
                        self.devConn.write(str.encode('/' + self.id + "v1000"+ "Z60000" + "V1000" + "A" + self.home + "R" + "\r"))
                        while waitFlag:
                                waitCheck1 = self.manual('/1Q')

                                if waitCheck1[3] == '`':
                                        waitFlag = False
                                else:
                                        time.sleep(0.1)
                                
                elif self.id == '2':
                        self.devConn.write(str.encode('/' + self.id + "v500"+ "Z30000" + "V500" + "A" + self.home + "R" + "\r"))
                        while waitFlag:
                                waitCheck2 = self.manual('/2Q')

                                if waitCheck2[3] == '`':
                                        waitFlag = False
                                else:
                                        time.sleep(0.1)
                        
                time.sleep(0.1)
                return response

        def moveStage(self, position):
                response = ''
                waitFlag = True
                
                if (int(position) >= int(self.pos)) or (int(position) <= int(self.neg)):
                        response = 'BAD\n' + response + 'Position out of range\n'
                        
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
                        response = 'BAD\n' + response + 'Position out of range\n'
                        
                else:
                        self.manual('/'+self.id+'A'+str(position)+'R')
                
                return response

        def manual(self, command):
                response = ''

                self.devConn.write(command + '\r')
                time.sleep(0.1)
                out = self.devConn.readline()
                
                if command[2] == 'Q':
                        response = out[:len(out)-3] + '\n'
                else:
                        response = out[4:len(out)-3] + '\n'
                
                return response