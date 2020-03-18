import SocketServer

def test():
    return 'test'

def print_it(data):
    print t

class MyTCPHandler(SocketServer.StreamRequestHandler,):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        
        print_it(self.data)
        
        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        self.wfile.write(self.data.upper())
            
if __name__ == "__main__":
    t = test()
    
    HOST, PORT = "192.168.1.198", 9997
    
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
