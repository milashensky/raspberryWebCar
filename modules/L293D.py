#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
#include <stdio.h>
# from PiZyPWM import PiZyPwm



try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. "
          "You can achieve this by using 'sudo' to run your script")

#include <pigpio.h>
import time
"""
   This code may be used to drive the Adafruit (or clones) Motor Shield.

   The code as written only supports DC motors.

   http://shieldlist.org/adafruit/motor

   The shield pinouts are

   D12 MOTORLATCH
   D11 PMW motor 1
   D10 Servo 1
   D9  Servo 2
   D8  MOTORDATA

   D7  MOTORENABLE
   D6  PWM motor 4
   D5  PWM motor 3
   D4  MOTORCLK
   D3  PWM motor 2

   The motor states (forward, backward, brake, release) are encoded using the
   MOTOR_ latch pins.  This saves four gpios.
"""

# typedef unsigned char uint8_t

def BIT(bit):
    return 1 << (bit)

# /* assign gpios to drive the shield pins */

# /*      Shield      Pi */

MOTORLATCH = 14
MOTORCLK   = 24
MOTORENABLE =25
MOTORDATA =  15

MOTOR_1_PWM = 5
MOTOR_2_PWM = 6
MOTOR_3_PWM = 7
MOTOR_4_PWM = 8

# /*
#    The only other connection needed between the Pi and the shield
#    is ground to ground. I used Pi P1-6 to shield gnd (next to D13).
# */
#
# /* assignment of motor states to latch */

MOTOR1_A = 2
MOTOR1_B = 3
MOTOR2_A = 1
MOTOR2_B = 4
MOTOR4_A = 0
MOTOR4_B = 6
MOTOR3_A = 5
MOTOR3_B = 7

FORWARD  = 1
BACKWARD = 2
BRAKE    = 3
RELEASE  = 4

class ATMotor:
    # pwm = None
    speed = 0
    pin = 0
    freq = 100 # DUNNO

    def __init__(self, pin, scheme):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)
        # self.pwm = PiZyPwm(self.freq, pin, scheme)
        # self.pwm.start(self.freq)

    def destroy(self):
        if self.pin:
            GPIO.output(self.pin, 0)
        # if self.pwm:
        #     self.pwm.stop()


class MotorControl:
    latch_state = None

    def latch_tx(self):
       GPIO.output(MOTORLATCH, GPIO.LOW)
       GPIO.output(MOTORDATA, GPIO.LOW)

       for i in range(0, 8):
          # time.sleep(0.01) # 10 micros delay

          GPIO.output(MOTORCLK, GPIO.LOW)

          if self.latch_state & BIT(7-i):
              GPIO.output(MOTORDATA, GPIO.HIGH)
          else:
              GPIO.output(MOTORDATA, GPIO.LOW)
          time.sleep(0.01)  # 10 micros delay
          GPIO.output(MOTORCLK, GPIO.HIGH)
       GPIO.output(MOTORLATCH, GPIO.HIGH)
       return True


    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTORLATCH,  GPIO.OUT)
        GPIO.setup(MOTORENABLE, GPIO.OUT)
        GPIO.setup(MOTORDATA,   GPIO.OUT)
        GPIO.setup(MOTORCLK,    GPIO.OUT)

        GPIO.setup(MOTOR_1_PWM, GPIO.OUT)
        GPIO.setup(MOTOR_2_PWM, GPIO.OUT)
        GPIO.setup(MOTOR_3_PWM, GPIO.OUT)
        GPIO.setup(MOTOR_4_PWM, GPIO.OUT)

        GPIO.output(MOTOR_1_PWM, 0) # PWM in ideal
        GPIO.output(MOTOR_2_PWM, 0) # PWM in ideal
        GPIO.output(MOTOR_3_PWM, 0) # PWM in ideal
        GPIO.output(MOTOR_4_PWM, 0) # PWM in ideal
        self.latch_state = 0
        self.latch_tx()
        GPIO.output(MOTORENABLE, GPIO.LOW)
        return None

    def DCMotorInit(self, num):
        if num == 1:
          self.latch_state &= ~BIT(MOTOR1_A) & ~BIT(MOTOR1_B)
        elif num == 2:
          self.latch_state &= ~BIT(MOTOR2_A) & ~BIT(MOTOR2_B)
        elif num == 3:
          self.latch_state &= ~BIT(MOTOR3_A) & ~BIT(MOTOR3_B)
        elif num == 4:
          self.latch_state &= ~BIT(MOTOR4_A) & ~BIT(MOTOR4_B)
        else:
          return
        self.latch_tx()
        print("Latch=%s"% self.latch_state)
        return True

    def DCMotorRun(self, motornum, cmd):
        a = b = 0
        if motornum == 1:
            a = MOTOR1_A
            b = MOTOR1_B
        elif motornum == 2:
            a = MOTOR2_A
            b = MOTOR2_B
        elif motornum == 3:
            a = MOTOR3_A
            b = MOTOR3_B
        elif motornum == 4:
            a = MOTOR4_A
            b = MOTOR4_B
        else:
            return

        if cmd == FORWARD:
            self.latch_state |=  BIT(a)
            self.latch_state &= ~BIT(b)
        elif cmd == BACKWARD:
            self.latch_state &= ~BIT(a)
            self.latch_state |=  BIT(b)
        elif cmd == RELEASE:
            self.latch_state &= ~BIT(a)
            self.latch_state &= ~BIT(b)
        else:
            return

        self.latch_tx()
        print("Latch=%s" % self.latch_state)
        return True

    def runMotor(self, num, speed=100, direction=True):
        pin = None
        if num == 1:
            pin = MOTOR_1_PWM
        elif num == 2:
            pin = MOTOR_2_PWM
        elif num == 3:
            pin = MOTOR_3_PWM
        elif num == 4:
            pin = MOTOR_4_PWM
        else:
            return None
        if pin:
            GPIO.output(pin, speed)
            if direction:
                self.DCMotorRun(num, FORWARD)
            else:
                self.DCMotorRun(num, BACKWARD)

    def stopMotor(self, num):
        self.DCMotorRun(num, RELEASE)

    def stopAllMotors(self):
        self.DCMotorRun(1, RELEASE)
        self.DCMotorRun(2, RELEASE)
        self.DCMotorRun(3, RELEASE)
        self.DCMotorRun(4, RELEASE)

    def test(self):
        i = 60
        # while i < 160:
        #     GPIO.output(MOTOR_3_PWM, i) # PWM in ideal
        #     GPIO.output(MOTOR_4_PWM, 220-i) # PWM in ideal
        #
        #     self.DCMotorRun(3, FORWARD)
        #     self.DCMotorRun(4, BACKWARD)
        #
        #     time.sleep(2)
        #
        #     self.DCMotorRun(3, RELEASE)
        #     self.DCMotorRun(4, RELEASE)
        #
        #     time.sleep(2)
        #
        #     GPIO.output(MOTOR_4_PWM, i) # PWM in ideal
        #     GPIO.output(MOTOR_3_PWM, 220-i) # PWM in ideal
        #
        #     self.DCMotorRun(3, BACKWARD)
        #     self.DCMotorRun(4, FORWARD)
        #
        #     time.sleep(2)
        #
        #     self.DCMotorRun(3, RELEASE)
        #     self.DCMotorRun(4, RELEASE)
        #
        #     time.sleep(2)
        #     i += 20
        self.runMotor(1, i)
        self.runMotor(2, i)
        self.runMotor(3, i)
        self.runMotor(4, i)
        time.sleep(2)
        self.stopMotor(3)
        self.stopMotor(4)
        time.sleep(1)
        self.runMotor(3, i, False)
        self.runMotor(4, i, False)
        time.sleep(2)
        self.stopMotor(3)
        self.stopMotor(4)
        time.sleep(1)
        self.runMotor(3, i, True)
        self.runMotor(4, i, False)
        time.sleep(2)
        self.stopMotor(3)
        self.stopMotor(4)
        time.sleep(1)
        self.runMotor(4, i, True)
        self.runMotor(3, i, False)
        time.sleep(2)
        self.stopAllMotors()
        time.sleep(1)
        a.runMotor(2, 100)
        a.runMotor(1, 100, False)
        a.runMotor(3, 100)
        a.runMotor(4, 100, False)
        time.sleep(2)
        self.stopAllMotors()
        time.sleep(1)
        a.runMotor(2, 100, False)
        a.runMotor(1, 100)
        a.runMotor(3, 100, False)
        a.runMotor(4, 100)
        time.sleep(2)
        GPIO.output(MOTOR_1_PWM, 0) # PWM in ideal
        GPIO.output(MOTOR_2_PWM, 0) # PWM in ideal
        GPIO.output(MOTOR_4_PWM, 0) # PWM in ideal
        GPIO.output(MOTOR_3_PWM, 0) # PWM in ideal


        self.stopMotor(1)
        self.stopMotor(2)
        self.stopMotor(3)
        self.stopMotor(4)

        return 'Done'

# a = MotorControl()
# a.test()
# GPIO.cleanup()
