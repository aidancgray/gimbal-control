#!/usr/bin/python
import pigpio
import time
import SocketServer

class MyTCPHandler(SocketServer.StreamRequestHandler):

    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    
    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        self.wfile.write(self.data.upper())

def main():

    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
    
    pi = pigpio.pi()

    L930 = 17
    L970 = 27
    L1050 = 22
    L1070 = 5
    L1085 = 6
    L1200 = 13
    L1300 = 26

    flag = True
    
    while flag:
        
        LED = raw_input('LED (930, 970, 1070, 1085, 1200, 1300): ')

        if LED == 'q':
            flag = False
        else:
            dutycycle = raw_input('Duty cycle (%): ')

            if dutycycle == 'q':
                flag = False
            elif LED == '930':
                pi.set_PWM_dutycycle(L930, 255 * dutycycle)
            elif LED == '970':
                pi.set_PWM_dutycycle(L970, 255 * dutycycle)
            elif LED == '1050':
                pi.set_PWM_dutycycle(L1050, 255 * dutycycle)
            elif LED == '1070':
                pi.set_PWM_dutycycle(L1070, 255 * dutycycle)
            elif LED == '1085':
                pi.set_PWM_dutycycle(L1085, 255 * dutycycle)
            elif LED == '1200':
                pi.set_PWM_dutycycle(L1200, 255 * dutycycle)
            elif LED == '1300':
                pi.set_PWM_dutycycle(L1300, 255 * dutycycle)
            else:
                print 'Please enter a valid LED'
            
    pi.stop()

if __name__ == "__main__":
    main()
