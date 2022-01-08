#!/usr/bin/env python3
import time
from pylgbst.hub import MoveHub, EncodedMotor, Voltage, COLOR_RED, COLOR_BLUE
from pylgbst import get_connection_bleak
import pygame
import subprocess


ADDRESS = '00:16:53:XX:XX:XX'

subprocess.call(('bluetoothctl', 'disconnect', ADDRESS))

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)

conn = get_connection_bleak(hub_mac=ADDRESS)
hub = MoveHub(conn)

current_angle = None

def callback(angle):
    global current_angle
    current_angle = angle

hub.motor_external.subscribe(callback, mode=EncodedMotor.SENSOR_ANGLE)

def main():
    while True:
        forward = joystick.get_axis(1) * -1
        leftright = (joystick.get_axis(0) + 1) / 2
        if forward > -0.2 and forward < 0.2:
            if leftright > 0.4 and leftright < 0.6:
                hub.motor_AB.stop()
            else:
                hub.motor_A.start_speed(joystick.get_axis(0) * 0.5)
                hub.motor_B.start_speed(joystick.get_axis(0) * -0.5)
        else:
            if leftright > 0.3 and leftright < 0.7:
                leftright = 0.5
            hub.motor_A.start_speed(forward * leftright * 1)
            hub.motor_B.start_speed(forward * (1 - leftright) * 1)
        desired_angle = joystick.get_axis(3) * 50
        if current_angle is not None:
            if abs(current_angle - desired_angle) > 5:
                hub.motor_external.goto_position(int(desired_angle), 0.9)

        time.sleep(0.05)
        pygame.event.pump()

try:
    main()
finally:
    pygame.quit()
