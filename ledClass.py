import time
import pigpio

class LED:
    def __init__(self, piGPIO, LEDs, LEDList):
        self.piGPIO = piGPIO  # Pi GPIO Connection
        self.LEDs = LEDs  # list of all available LED wavelengths
        self.LEDList = LEDList # List of LEDs, with their pins, and power %

    ### LED Control Method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LEDControl(self, led, dutycycle):
        # If DC = 0, turn on all GPIO pins and set all to 0
        if int(dutycycle) == 0:
            for i in range(len(self.LEDList)):
                self.piGPIO.set_mode(self.LEDList[i][1], pigpio.OUTPUT)  # set all pins to output mode
                self.piGPIO.set_PWM_dutycycle(self.LEDList[i][1], 0)

            response = ''

        else:
            # Loop through list of LEDs to find which pin to use
            for i in range(len(self.LEDList)):
                self.piGPIO.set_mode(self.LEDList[i][1], pigpio.INPUT)  # set all pins to input mode
                if led == self.LEDList[i][0]:
                    pin = self.LEDList[i][1]
                    self.LEDList[i][2] = dutycycle
                        
            response = ''
            self.piGPIO.set_mode(pin, pigpio.OUTPUT)
            self.piGPIO.set_PWM_dutycycle(pin, 255 * (float(dutycycle)/100))
        

        return response

    ### LED Command Parser ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LEDParse(self, command):
        response = ''
        
        if len(command) >= 2 and command[1] != '?':
                led = command[1]

                if led not in self.LEDs:
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
                            
                    response = response + self.LEDControl(led, dutycycle)
            
        elif command[1] == '?':
            response = response + '-LED-|-Dutycycle-\n'

            for n in range(len(self.LEDList)):
                try:
                    response = response + self.LEDList[n][0] + ' | ' + str(int(float(self.piGPIO.get_PWM_dutycycle(self.LEDList[n][1])) / 2.55)) + '%\n'
                except:
                    response = response + self.LEDList[n][0] + ' | ' + '0' + '%\n'                 
        else:
            response = 'BAD\n' + response + 'No LED specified'
        
        return response
