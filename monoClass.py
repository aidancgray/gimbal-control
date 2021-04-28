import time
import pigpio

class Mono:
    def __init__(self, piGPIO, monoGPIO, devConn, monoStepMode):
        self.piGPIO = piGPIO  # Pi GPIO connection
        self.MonoGPIO = monoGPIO  # the GPIO pin for the lamp
        self.devConn = devConn  # Device Connection
        self.monoStepMode = monoStepMode  # Microstep Mode 1/#
        self.monoFit = (4.003465 * self.monoStepMode, 109.8399 * self.monoStepMode)  # Linear Fit Tuple for converting steps to wavelength

    ### Monochromator Control Method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def MonoControl(self, wavelength):
        response = ''
        absPosition = int(round(wavelength * self.monoFit[0] + self.monoFit[1]))  # convert wavelength -> motor position
        response = self.manual('/1A' + str(absPosition) + 'R\r')  # send monochromator abs position 
        
        waitFlag = True
        while waitFlag:
            waitCheck = self.manual('/1Q')

            if waitCheck[3] == '`':
                waitFlag = False
            else:
                time.sleep(0.1)

        return response


    ### Monochromator Power On/Off ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def MonoPower(self, state):
        if state == 1:
            self.piGPIO.set_mode(self.MonoGPIO, pigpio.OUTPUT)
            self.piGPIO.write(self.MonoGPIO, 1)
                
        elif state == 0:
            self.piGPIO.set_mode(self.MonoGPIO, pigpio.OUTPUT)
            self.piGPIO.write(self.MonoGPIO, 0)
            self.piGPIO.set_mode(self.MonoGPIO, pigpio.INPUT)
                
        else:
            raise IOError('MonoPower accepts 1 or 0 as input')


    ### Monochromator Command Parser ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def MonoParse(self, command):
        response = ''

        if len(command) >= 2 and command[1] != '?' and command[1] != 'home' and command[1] != 'on' and command[1] != 'off' and command[1][0] != '/':
            monoCommand = command[1]

            try:
                wavelengthSet = float(monoCommand)

                if wavelengthSet >= 0 and wavelengthSet <= 1750:
                    response = self.MonoControl(wavelengthSet)
                else:
                    response = 'BAD\n' + response + 'wavelength range: 0-1750nm'

            except ValueError:
                response = 'BAD\n' + response + 'command structure is: mono [wavelength in nm]'

        elif command[1] == '?':
            self.devConn.write('/1?0' + '\r')  # query monochromator position 
            time.sleep(0.1)
            out = self.devConn.readline()

            monoPosition = out.split('`')[1].split('\x03')[0]  # strip output
            wavelengthGet = round((float(monoPosition) - self.monoFit[1]) / self.monoFit[0], 2)  # convert to wavelength

            monoPower = self.piGPIO.read(self.MonoGPIO)
            if monoPower == 0:
                response = 'OFF\n' + str(wavelengthGet) + '\n'
            elif monoPower == 1:
                response = 'ON\n'  + str(wavelengthGet) + '\n'
            else:
                response = 'NA\n'  + str(wavelengthGet) + '\n'

        elif command[1] == 'home':
            self.devConn.write('/1Z40000V200P447V800R\r')
            time.sleep(0.1)
            out = self.devConn.readline()
            
            waitFlag = True
            while waitFlag:
                waitCheck = self.manual('/1Q')

                if waitCheck[3] == '`':
                    waitFlag = False
                else:
                    time.sleep(0.1)
        
        elif command[1] == 'on':
            self.MonoPower(1)
        
        elif command[1] == 'off':
            self.MonoPower(0)

        elif command[1][0] == '/':
            response = self.manual(command[1])

            waitFlag = True
            while waitFlag:
                waitCheck = self.manual('/1Q')

                if waitCheck[3] == '`':
                    waitFlag = False
                else:
                    time.sleep(0.1)

        else:
            response = 'BAD\n' + response + 'No wavelength specified'
        
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