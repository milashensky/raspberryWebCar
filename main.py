import json
import sys
import os
import time
import math

from flask import Flask, send_from_directory, request
from flask import render_template
from modules.L293D import MotorControl

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
a = MotorControl()
app = Flask(__name__)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/control/', methods=['POST'])
def parse_request():
    response = request.data
    if response:
        data = json.loads(response.decode())
        print(data)
        direction = data.get('direction', '')
        if 'up' in direction:
            a.stopAllMotors()

            a.runMotor(2, 100)
            a.runMotor(1, 100)

            a.runMotor(3, 100)
            a.runMotor(4, 100)
        elif 'down' in direction:
            a.stopAllMotors()

            a.runMotor(2, 100, False)
            a.runMotor(1, 100, False)

            a.runMotor(3, 100, False)
            a.runMotor(4, 100, False)
        elif 'left' in direction:
            a.stopAllMotors()

            a.runMotor(2, 100)
            a.runMotor(1, 100, False)
            a.runMotor(3, 100)
            a.runMotor(4, 100, False)
        elif 'right' in direction:
            a.stopAllMotors()

            a.runMotor(2, 100, False)
            a.runMotor(1, 100)

            a.runMotor(3, 100, False)
            a.runMotor(4, 100)
        elif direction.strip() == '':
            a.stopAllMotors()

        # amspi.run_dc_motors([2, 3], clockwise=rightCl, speed=)
        # amspi.run_dc_motors([1, 4], clockwise=leftCl, speed=round(left * speed * 100 / 3))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
