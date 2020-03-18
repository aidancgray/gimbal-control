import socket
import sys

HOST, PORT = "192.168.1.198", 9999
#data = " ".join(sys.argv[1:])

print("Send commands below. Type Q to quit:")
    
flag = True
while flag:

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        
        data = input('$ ')
        
        if data.upper() == 'Q':
            flag = False
        else:
            sock.sendall(bytes(data + "\n", "utf-8"))
            
            # Receive data from the server and shut down
            received = str(sock.recv(1024), "latin-1")
            print("Sent:     {}".format(data))
            print("Received: {}".format(received))

        sock.close()
