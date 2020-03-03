from pymavlink import mavutil
from multiprocessing import Process, Queue
import time
from sys import exit
import serial
import signal
from ProcessQueue import ProcessQueue
from DepthControllerProcess import DepthControllerProcess
from NavigateControllerProcess import NavigateControllerProcess
from DriveObject import DriveObject
from DepthObject import DepthObject

from Arduino import Arduino
from ArduinoComms import *

import random
import math

# Pwm channel pins
# 0 - pitch
# 1 - roll
# 2 - up
# 3 - yaw
# 4 - forward
# 5 - lateral
# 6 - camera pan
# 7 - camera tilt
# 8 - lights 1 level


TURN_BUFFER = 2
PING_FORWARD_STOP = 2000
PING_EXPIRE_TIME = 3 # seconds
PING_CONF = 60

startMarker = 60
endMarker = 62

def handler(signum, frame):
    print('Handle Ctrl-C')
    handle_exit()
    exit()

def handle_exit():
    print("Exiting")
    exit()

if __name__=='__main__':
    signal.signal(signal.SIGINT, handler)
    mavlink = mavutil.mavlink_connection('udpin:0.0.0.0:15000')
    # Wait a heartbeat before sending commands
    mavlink.wait_heartbeat()
    serial = serial.Serial('COM3', 115200, timeout=0)
    arduino = Arduino(serial, PING_FORWARD_STOP, PING_EXPIRE_TIME, PING_CONF)
    process_queues = ProcessQueue()
    depth_obj = DepthObject('', '')
    drive_obj = DriveObject('', '')
    armed = False ## processes only run when armed

    while True:
        if not armed:
            cmd_message = input('please arm the AUV')
            if cmd_message == 'arm':
                arm = True
                depth_controller = DepthControllerProcess(depth_obj, mavlink, process_queues)
                nav_controller = NavigateControllerProcess(drive_obj, mavlink, process_queues)
                depth_controller.start()
                nav_controller.start()
                print('**AUV Armed**')
        else:
            cmd_message = input('Waiting For Command: ')
            if cmd_message == 'disarm':
                arm = False
                depth_controller.terminate()
                nav_controller.terminate()
                print('**AUV Disarmed**')
            if cmd_message == 'depth' or cmd_message == 'bottom_hold':
                depth = input('Depth: ')
                msg = (cmd_message, depth)
                process_queues.ui_depth.put(msg)
            elif cmd_message == 'forward' or cmd_message == 'backward':
                distance = input('Time: ') # or until near object/something
                msg = (cmd_message, distance)
                process_queues.ui_nav.put(msg)
            elif cmd_message == 'yaw':
                process_queues.ui_nav.put(cmd_message)
            elif cmd_message == 'roomba':
                distance = input('Time: ') # or until near object/something
                msg = (cmd_message, distance)
                process_queues.ui_nav.put(msg)
            elif cmd_message == 'run mission':
                process_queues.ui_depth.put('bottom_hold 1.5')
                process_queues.ui_nav.put('roomba 30 1 10000')
            elif cmd_message == 'help':
                print("arm - arm the motors")
                print("disarm - disarm the motors")
                print("yaw <0-100% throttle> <relative degrees> - turn robot")
                print("forward <0-100% throttle> - drive forward for x seconds")
                print("reverse <0-100% throttle> - drive reverse for x seconds")
                print("roomba <0-100% throttle> - execute roomba search pattern for a given time")
                print("depth <0-100% throttle> <target depth (m)> - dive to given depth")
                print("bottomHold <0-100% throttle> <Distance from bottom(m)>")
                print("q - quit the program")
            elif cmd_message == 'quit' or cmd_message == 'q':
                depth_controller.terminate()
                nav_controller.terminate()
                break
            





    # STATE SPACE::
    # While scanning for lionfish
        # Roomba process
    # if see lionfish
        # movre toward lionfish
    # if emergence kill lionfish and roomba search
    # if end of mission go home
    # arduino_comm.start()
    # print('here')
    # time.sleep(10)
    # arduino_comm.terminate()
    # Create the connection
    # mavlink = mavutil.mavlink_connection('udpin:0.0.0.0:15000')
    # Wait a heartbeat before sending commands
    # mavlink.wait_heartbeat()


    #Start arduino Process
    #start camera process,
        # including object detection and tracking processes

