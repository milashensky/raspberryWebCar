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
        # print(data)
        left = math.fabs(data.get('left', 0))
        right = math.fabs(data.get('right', 0))
        speed = data.get('speed', 0)
        direction = data.get('direction', True)
        if not speed:
            a.stopMotors()
        else:
            # a.runMotor(2, round(right * speed * 100 / 3), direction)
            # a.runMotor(3, round(right * speed * 100 / 3), direction)
            a.runMotors([1, 4], round(left * speed * 100 / 3), direction)
            a.runMotors([2, 3], round(right * speed * 100 / 3), direction)

        # amspi.run_dc_motors([2, 3], clockwise=rightCl, speed=)
        # amspi.run_dc_motors([1, 4], clockwise=leftCl, speed=round(left * speed * 100 / 3))
        time.sleep(0.5)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
