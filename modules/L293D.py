#!/usr/bin/env python
import os
import RPi.GPIO as GPIO
from time import sleep

ENABLE = 0
FORWARD = 1
BACKWARD = 2

def PWM(pin, val):
    cmd = 'echo "%d=%.2f" > /dev/pi-blaster' % ( pin, val / 100)
    # print(cmd)
    os.system(cmd)


class MotorControl:
    MOTORS = {
        1: {
            ENABLE:  5,
            FORWARD: 26,
            BACKWARD: 13,
        },
        2: {
            ENABLE:  22,
            FORWARD: 17,
            BACKWARD: 27,
        },
        3: {
            ENABLE:  10,
            FORWARD: 9,
            BACKWARD: 11,
        },
        4: {
            ENABLE:  7,
            FORWARD: 25,
            BACKWARD: 8,
        },
    }

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.initMotor(1)
        self.initMotor(2)
        self.initMotor(3)
        self.initMotor(4)

    def initMotor(self, num):
        motor = self.MOTORS[num]
        GPIO.setup(motor[FORWARD], GPIO.OUT)
        GPIO.setup(motor[BACKWARD], GPIO.OUT)
        # GPIO.setup(motor[ENABLE], GPIO.OUT)
        PWM(motor[ENABLE], 0)


    def runMotor(self, num, speed=100, direction=True):
        motor = self.MOTORS[num]
        if direction:
            GPIO.output(motor[FORWARD], 1)
            GPIO.output(motor[BACKWARD], 0)
        else:
            GPIO.output(motor[FORWARD], 0)
            GPIO.output(motor[BACKWARD], 1)
        # GPIO.output(motor[ENABLE], 1)
        PWM(motor[ENABLE], speed)

    def stopMotor(self, num):
        # GPIO.output(self.MOTORS[num][ENABLE], 0)
        PWM(self.MOTORS[num][ENABLE], 0)

    def releaseMotor(self, num):
        motor = self.MOTORS[num]
        self.stopMotor(num)
        GPIO.output(motor[BACKWARD], 0)
        GPIO.output(motor[FORWARD], 0)
        # GPIO.output(motor[ENABLE], 0)

    def stopMotors(self, nums=[1,2,3,4]):
        for i in nums:
            self.stopMotor(i)

    def runMotors(self, nums=[1,2,3,4], speed=100, direction=True):
        for i in nums:
            self.runMotor(i, speed, direction)

    def releaseMotors(self, nums=[1,2,3,4]):
        for i in nums:
            self.releaseMotor(i)


# a = MotorControl()

# for i in range(1, 5):
#     a.runMotor(i, 40, True)
#     sleep(1)
#     a.runMotor(i, 40, False)
#     sleep(1)
#     a.stopMotor(i)
#
#
# a.runMotors(speed=100)
# sleep(3)
# a.stopMotors()
# sleep(1)
# a.runMotors(speed=70, direction=False)
# sleep(3)
# a.runMotors(speed=20)
# sleep(1)
# a.releaseMotors()
