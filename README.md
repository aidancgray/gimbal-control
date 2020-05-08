# gimbal-control

TCP Server for controlling the collimator gimbal for testing the PFS NIRCAM.

##### Files:
- gimbal_server.py : The server that runs on the Raspberry Pi 3B.
- TCPClient3.py : A simple universal client to talk to the gimbal server.

##### XY Stage Control Commands:
The XY stages are controlled by absolute microsteps.
Commands are in the form of 'move [X] [Y]'. For example, 'move 1000 2000'.

##### LED Control Commands:
The LEDs are controlled one at a time.
Commands are in the form of 'led [wavelength (nm)] [dutycyle (%)]'. For example, 'led 970 50'.

