#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
#include <stdio.h>
from PiZyPWM import PiZyPwm



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

# typedef unsigned char uint8_t;

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
    pwm = None
    speed = 0
    pin = 0
    freq = 100 # DUNNO

    def __init__(self, pin, scheme):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)
        self.pwm = PiZyPwm(self.freq, pin, scheme)
        self.pwm.start(self.freq)

    def destroy(self):
        if self.pin:
            GPIO.output(self.pin, 0)
        if self.pwm:
            self.pwm.stop()


class MotorContol:
    latch_state = 0
    scheme = GPIO.BCM
    Motors = {
        1: None,
        2: None,
        3: None,
        4: None,
    }

    def latch_tx(self):
        GPIO.output(MOTORLATCH, GPIO.LOW)
        GPIO.output(MOTORDATA, GPIO.LOW)

        for i in range(0, 8):
            # time.sleep(0.01) # 10 micros delay

            GPIO.output(MOTORCLK, GPIO.LOW)

            if self.latch_state & BIT(7 - i):
                GPIO.output(MOTORDATA, GPIO.HIGH)
            else:
                GPIO.output(MOTORDATA, GPIO.LOW)
            # time.sleep(0.01)  # 10 micros delay
            GPIO.output(MOTORCLK, GPIO.HIGH)
        GPIO.output(MOTORLATCH, GPIO.HIGH)
        return True


    def __init__(self, pins=[MOTOR_1_PWM, MOTOR_2_PWM, MOTOR_3_PWM, MOTOR_4_PWM], scheme=GPIO.BCM):
        self.scheme = scheme
        GPIO.setmode(scheme)


        GPIO.setup(MOTORLATCH,  GPIO.OUT)
        GPIO.setup(MOTORENABLE, GPIO.OUT)
        GPIO.setup(MOTORDATA,   GPIO.OUT)
        GPIO.setup(MOTORCLK,    GPIO.OUT)

        for i in range(0, 4):
            if pins[i]:
                self.Motors[i+1] = ATMotor(pin=pins[i], scheme=scheme)

        self.Motors[3] = ATMotor(MOTOR_3_PWM, scheme)
        self.Motors[4] = ATMotor(MOTOR_4_PWM, scheme)

        self.latch_state = 0
        self.latch_tx()
        GPIO.output(MOTORENABLE, GPIO.LOW)

        for k, v in self.Motors.items():
            if v:
                self.DCMotorInit(k)
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
            return None
        self.latch_tx()
        # print("Latch=%s"% self.latch_state)
        motor = self.getMotor(num)
        motor.pwm = PiZyPwm(motor.freq, motor.pin, self.scheme)
        motor.pwm.start(0) # DUNNO
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
        # print("Latch=%s" % self.latch_state)
        return True

    def runMotor(self, num, speed=140, forward=True):
        motor = self.getMotor(num)
        if motor:
            if speed < 45:
                speed = 45
            if speed > 160:
                speed = 160
            if speed and motor.speed != speed:
                motor.speed = speed
                motor.pwm.changeDutyCycle(motor.speed)
            if forward:
                self.DCMotorRun(num, FORWARD)
            else:
                self.DCMotorRun(num, BACKWARD)
        return True

    def stopMotor(self, num):
        motor = self.getMotor(num)
        if motor:
            # if motor.speed:
            #
            motor.speed = 0
            self.DCMotorRun(num, RELEASE)
        return True

    def releaseMotor(self, num):
        motor = self.getMotor(num)
        if motor:
            if motor.speed:
                self.stopMotor(num)
            time.sleep(2)
            motor.destroy()
        return True


    def getMotor(self, num):
        if self.Motors[num]:
            return self.Motors[num]
        else:
            return None



    def main(self):
        # MIN 45 STABLE
        i = 45
        # self.DCMotorInit(1)
        # self.DCMotorInit(2)
        # self.DCMotorInit(3)
        # self.DCMotorInit(4)
        m3 = self.Motors[3].pwm
        m4 = self.Motors[4].pwm
        #
        # m3.start(0)
        # m4.start(0)

        while i < 50:
            print('I: %s' % i)
            # GPIO.output(MOTOR_3_PWM, GPIO.HIGH)
            # GPIO.output(MOTOR_4_PWM, GPIO.HIGH)

            m4.changeDutyCycle(i)
            m3.changeDutyCycle(i+60)

            self.DCMotorRun(3, FORWARD)
            self.DCMotorRun(4, FORWARD)
            time.sleep(2)

            self.DCMotorRun(3, RELEASE)
            self.DCMotorRun(4, RELEASE)

            time.sleep(2)

            m4.changeDutyCycle(i)
            # m3.changeDutyCycle(i)

            # GPIO.output(MOTOR_4_PWM, i)
            # GPIO.output(MOTOR_3_PWM, 220-i)

            self.DCMotorRun(3, BACKWARD)
            self.DCMotorRun(4, BACKWARD)

            time.sleep(2)

            self.DCMotorRun(3, RELEASE)
            self.DCMotorRun(4, RELEASE)
            time.sleep(2)
            i += 5

        GPIO.output(MOTOR_4_PWM, 0)
        GPIO.output(MOTOR_3_PWM, 0)

        self.DCMotorRun(3, RELEASE)
        self.DCMotorRun(4, RELEASE)
        m3.stop()
        m4.stop()

        return 'Done'


# a = MotorContol()
# a.DCMotorInit(1)
# a.DCMotorInit(2)
# a.DCMotorInit(3)
# a.DCMotorInit(4)
# # a.run_motor(3, 220-160, FORWARD)
# # a.run_motor(4, 160, FORWARD)
# # time.sleep(2)
# # a.stop_motor(3)
# # a.stop_motor(4)
# # time.sleep(1)
#
# # a.main()
#
# a.runMotor(3, 45)
# a.runMotor(4, 100, False)
# a.runMotor(1)
# a.runMotor(2)
# time.sleep(2)
# a.stopMotor(3)
# a.stopMotor(4)
# time.sleep(2)
# a.runMotor(3, 100, False)
# a.runMotor(4, 45)
# time.sleep(2)
# a.stopMotor(3)
# a.stopMotor(4)
# a.stopMotor(2)
# a.stopMotor(1)
# a.releaseMotor(1)
# a.releaseMotor(2)
# a.releaseMotor(3)
# a.releaseMotor(4)
# GPIO.cleanup()
