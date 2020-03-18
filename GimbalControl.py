#!/usr/bin/python3.7

# Name: GimbalControl.py
# Project: PFS - NIR Camera Testing
# Author: Aidan Gray
# Contact: aidan.gray@idg.jhu.edu
# Date: 9/17/2019
# Description:
#
# Control GUI for the detector testing gimbal system.
# Options for control:
# - homing Y & Z stages,
# - choice menu for pointing direction, and
# - manual command issuing to EZHR stepper motor controller.

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys, serial, time, logging

# Outputs text to GUI output log
class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

# Main GUI class
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.t = connect()
        
        # (Controller Name, EZHR Address, Current Location, Home Location, Positive Location, Negative Location)
        self.xstage = Stage('X-Axis', '1', 0, '25000', '1000', '55000')
        self.ystage = Stage('Y-Axis', '2', 0, '15000', '1000', '25000') #MAX ABSOLUTE = 30,000

        self.t.write(str.encode("/1V3700R\r"))
        self.t.write(str.encode("/2V2000R\r"))
        
        # Create the 3 buttons for homing the axes
        homeXbutton = QPushButton("Home X-Axis")
        homeXbutton.pressed.connect(lambda: self.xstage.homeStage(self.t))
        homeYbutton = QPushButton("Home Y-Axis")
        homeYbutton.pressed.connect(lambda: self.ystage.homeStage(self.t))
        homeBbutton = QPushButton("Home Both Axes")
        homeBbutton.pressed.connect(lambda: self.xstage.homeStage(self.t))
        homeBbutton.pressed.connect(lambda: self.ystage.homeStage(self.t))

        # this is just a horizontal line separator for layouts
        lineH = QFrame();
        lineH.setFrameShape(QFrame.HLine)
        lineH.setFrameShadow(QFrame.Sunken)

        lineH2 = QFrame();
        lineH2.setFrameShape(QFrame.HLine)
        lineH2.setFrameShadow(QFrame.Sunken)

        # this is just a vertical line separator for layouts
        lineV = QFrame();
        lineV.setFrameShape(QFrame.VLine)
        lineV.setFrameShadow(QFrame.Sunken)

        main_layout = QVBoxLayout()
        sub_layout1 = QHBoxLayout()
        sub_layout1a = QVBoxLayout()
        sub_layout1b = QGridLayout()
        sub_layout2 = QGridLayout()
        sub_layout3 = QVBoxLayout()

        sub_layout1a.setContentsMargins(200,10,200,10)
        sub_layout1b.setContentsMargins(100, 10, 100, 10)

        # Homing Buttons ################################################################################
        sub_layout1a.addWidget(homeXbutton)
        sub_layout1a.addWidget(homeYbutton)
        sub_layout1a.addWidget(homeBbutton)

        # Choice Pointing ###############################################################################
        choice_label = QLabel("Choose a pointing position:")
        sub_layout1b.addWidget(choice_label, 0, 1, 1, 3, Qt.AlignCenter)

        radio_list = []
        
        for n in range(10):
            rad = QRadioButton(str(n+1))
            rad.setChecked(False)
            rad.toggled.connect(self.buttonStateChoice)
            radio_list.append(rad)
        
        n = 0;
        for i in range(3):
            for j in range(3):
                sub_layout1b.addWidget(radio_list[n], i+1, j+1, 1, 1, Qt.AlignCenter)
                n+=1

        sub_layout1.addLayout(sub_layout1a)
        sub_layout1.addWidget(lineV)
        sub_layout1.addLayout(sub_layout1b)

        # Manual Commands ################################################################################
        manual_control_label = QLabel("Enter an EZHR Command for Manual Control:")
        manual_control_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        sub_layout2.addWidget(manual_control_label, 0, 0, 1, 2, Qt.AlignLeft | Qt.AlignVCenter)

        term_command_button = QPushButton("TERMINATE")
        term_command_button.setStatusTip("Terminates the current command")
        term_command_button.pressed.connect(self.onTerminate)
        sub_layout2.addWidget(term_command_button, 1, 0, 1, 1)
        
        self.manual_control_command = QLineEdit()
        self.manual_control_command.setPlaceholderText("Start command with /# . . .")
        sub_layout2.addWidget(self.manual_control_command, 1, 1, 1, 2)
        self.manual_control_command.returnPressed.connect(self.onCommandSend)
        
        send_command_button = QPushButton("Send")
        send_command_button.setStatusTip("Send a command directly to the EZHR Stepper Motor Controller")
        send_command_button.pressed.connect(self.onCommandSend)
        sub_layout2.addWidget(send_command_button, 1, 3, 1, 1)

        sub_layout2.setColumnStretch(1, 2)
        sub_layout2.setColumnStretch(2, 2)

        # Console Output ################################################################################
        log_label = QLabel("Console Output:")
        sub_layout3.addWidget(log_label)

        log_handler = QPlainTextEditLogger(self)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)
        sub_layout3.addWidget(log_handler.widget)

        # Main Layout ###################################################################################
        main_layout.addLayout(sub_layout1, 3)
        main_layout.addWidget(lineH)
        main_layout.addLayout(sub_layout2, 1)
        main_layout.addWidget(lineH2)
        main_layout.addLayout(sub_layout3, 2)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    # socket function to instantly terminate current stepper motor commands
    def onTerminate(self):
        logging.info("---TERMINATING CURRENT COMMAND---")
        manual(self.t, "/1T")
        manual(self.t, "/2T")
        
    # socket function to send a command to stepper motors
    def onCommandSend(self):
        logging.info(". . . Sending command . . .")
        logging.info(self.manual_control_command.text())
        manual(self.t, self.manual_control_command.text())
        self.manual_control_command.setText('')

    # socket function to catch which radio button is selected and issue motor command
    def buttonStateChoice(self):
        btn = self.sender()
        if btn.isChecked():
            logging.info("Moving to Position "+btn.text())
            choice(self.t, btn.text(), self.xstage, self.ystage)


# Connect to the RS485 port ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def connect():
    # Creation of the serial connection
    t = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        timeout=1,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False
    )

    t.close()
    t.open()

    # Confirm the connection is open
    if t.isOpen():
        logging.info(t.portstr + ' is open...')
        return t


# Manual Control ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def manual(t, strInput):

    n = t.write(str.encode(strInput + '\r'))
    out = t.readline()
    time.sleep(0.1)


# Choice control ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def choice(t, pos, xstage, ystage):

    if pos == '1':
        xstage.move(t, -1)
        ystage.move(t, 1)

    elif pos == '2':
        xstage.move(t, 0)
        ystage.move(t, 1)

    elif pos == '3':
        xstage.move(t, 1)
        ystage.move(t, 1)

    elif pos == '4':
        xstage.move(t, -1)
        ystage.move(t, 0)

    elif pos == '5':
        xstage.move(t, 0)
        ystage.move(t, 0)

    elif pos == '6':
        xstage.move(t, 1)
        ystage.move(t, 0)

    elif pos == '7':
        xstage.move(t, -1)
        ystage.move(t, -1)

    elif pos == '8':
        xstage.move(t, 0)
        ystage.move(t, -1)

    elif pos == '9':
        xstage.move(t, 1)
        ystage.move(t, -1)

    n = t.write(str.encode('/AR\r'))


# Stage class ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# axis: name of the stage (x, y, etc.)
# id: the address for the EZHR23 Controller
# loc: the current position of the stage (home, pos, neg)
# home: the "center" of the stage, or where it positions the collimator on-axis
# pos: the location of the positive position
# neg: the location of the negative position
class Stage:
    def __init__(self, axis, id, loc, home, pos, neg):
        self.axis = axis
        self.id = id
        self.loc = loc
        self.home = home
        self.pos = pos
        self.neg = neg

    def move(self, t, position):
        if self.loc == position:
            logging.info(self.axis + ': holding position')

        elif position == 0:
            logging.info(self.axis + ': moving to center')
            t.write(str.encode('/' + self.id + "A" + self.home + "R\r"))
            self.loc = 0

        elif position == 1:
            logging.info(self.axis + ': moving to +')
            t.write(str.encode('/' + self.id + "A" + self.pos + "R\r"))
            self.loc = 1

        elif position == -1:
            logging.info(self.axis + ': moving to -')
            t.write(str.encode('/' + self.id + "A" + self.neg + "R\r"))
            self.loc = -1
        time.sleep(0.1)

    def homeStage(self, t):
        logging.info("Homing the " + self.axis + " axis")
        if self.id == '1':
            t.write(str.encode('/' + self.id + "v2000"+ "Z50000" + "V3700" + "A" + self.home + "R" + "\r"))
        elif self.id == '2':
            t.write(str.encode('/' + self.id + "v2000"+ "Z30000" + "V2000" + "A" + self.home + "R" + "\r"))
        time.sleep(0.1)
        self.loc = 0


# Main function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Gimbal Controller")
    #window.showMaximized()
    window.show()
    app.exec_()
