import json
import sys
import os
import time
import math

from flask import Flask, send_from_directory, request
from flask import render_template
from modules.AMSpi import AMSpi

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
amspi = AMSpi()
amspi.set_74HC595_pins(21, 20, 16)
amspi.set_L293D_pins(5, 6, 13, 19)
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
        left = data.get('left', 0)
        right = data.get('right', 0)
        speed = data.get('speed', 0)
        leftCl = False
        rightCl = False
        if left < 0:
            leftCl = True
        if right < 0:
            rightCl = True
        amspi.stop_dc_motors([1,2,3,4])
        amspi.run_dc_motors([2, 3], clockwise=rightCl, speed=round(right * speed * 100 / 3))
        amspi.run_dc_motors([1, 4], clockwise=leftCl, speed=round(left * speed * 100 / 3))
        time.sleep(0.5)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
