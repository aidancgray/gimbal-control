import serial
import time

class Device:
	def __init__(self, devName):
		self.devName = devName
		self.devConn = self.connect(devName)

	### Connect to a RS485 port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def connect(self, usbPort):
		# Creation of the serial connection
		t = serial.Serial(
				port = usbPort,
				baudrate = 9600,
				timeout = 1,
				bytesize = serial.EIGHTBITS,
				parity = serial.PARITY_NONE,
				stopbits = serial.STOPBITS_ONE,
				xonxoff = False
		)
		
		t.close()
		t.open()
		
		# Confirm the connection is open
		if t.isOpen():
			print t.portstr + ' is open...'
			return t

	### Write directly to the serial device
	def write(self, writeData):
		resp = self.devConn.write(writeData)
		return resp

	### read directly from the serial device
	def readline(self):
		resp = self.devConn.readline()
		return resp

	### Manual Control ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	def manual(self, device, command):
		response = ''
		if device == 'stage':
			self.devConn.write(command + '\r')
			time.sleep(0.1)
			out = self.devConn.readline()
		
		elif device == 'mono':
			self.devConn.write(command + '\r')
			time.sleep(0.1)
			out = self.devConn.readline()
		
		if command[2] == 'Q':
			response = out[:len(out)-3] + '\n'
		else:
			response = out[4:len(out)-3] + '\n'
		
		return response