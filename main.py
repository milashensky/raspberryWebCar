import json
import sys
import os

from flask import Flask, send_from_directory, request
from flask import render_template
from modules.AMSpi import AMSpi

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
app = Flask(__name__)
amspi = AMSpi()
# Set PINs for controlling shift register (GPIO numbering)
amspi.set_74HC595_pins(21, 20, 16)
# Set PINs for controlling all 4 motors (GPIO numbering)
amspi.set_L293D_pins(5, 6, 13, 19)


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
            amspi.stop_dc_motors([1,2,3,4])
            amspi.run_dc_motors([amspi.DC_Motor_1, amspi.DC_Motor_3])
            amspi.run_dc_motors([amspi.DC_Motor_2, amspi.DC_Motor_4], clockwise=False)
        if 'down' in direction:
            amspi.stop_dc_motors([1,2,3,4])
            amspi.run_dc_motors([amspi.DC_Motor_1, amspi.DC_Motor_3], clockwise=False)
            amspi.run_dc_motors([amspi.DC_Motor_2, amspi.DC_Motor_4])
        if 'left' in direction:
            print('turn left')
            amspi.stop_dc_motors([1,2,3,4])
            amspi.run_dc_motors([2, 3])
            amspi.run_dc_motors([1, 4], clockwise=False)
        if 'right' in direction:
            amspi.stop_dc_motors([1,2,3,4])
            amspi.run_dc_motors([2, 3], clockwise=False)
            amspi.run_dc_motors([1, 4])
        if direction.strip() == '':
            amspi.stop_dc_motors([1,2,3,4])
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
