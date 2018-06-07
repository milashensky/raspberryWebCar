import json
import sys
import os
import time
import math

from flask import Flask, send_from_directory, request
from flask import render_template
from modules.L293D import MotorControl
from modules.utils import get_distance, get_angle, calculate_direction

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
a = MotorControl()
app = Flask(__name__)

MAX_DISTANCE_MOVE = 3
MAX_APPROVED_DISTANCE = 40
mode = "control"
source_lat = 0
source_lon = 0
my_lat = 0
my_lon = 0
last_lon = 0
last_lat = 0
locationThread = None


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/control/', methods=['POST'])
def parse_request():
    t.do_run = False
    t.join()
    mode = "control"
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
        locationThread = None
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/location/', methods=['POST'])
def parse_location():
    mode = "location"
    response = request.data
    if response:
        global source_lat
        global source_lon
        data = json.loads(response.decode())
        source_lat = float(data.get('lat', 0))
        source_lon = float(data.get('lon', 0))
        if not locationThread:
            def runner(*args, **kwargs):
                t = threading.currentThread()
                while getattr(t, "do_run", True):
                    processLocation(*args, **kwargs)

            locationThread = threading.Thread(
                target=runner,
                daemon=True
            )
            locationThread.start()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


def processLocation():
    if my_lat and my_lon and source_lat and source_lon:
        # while not last_lon not and last_lat:
        #     a.runMotors()
        #     time.sleep(2)
        #     a.stopMotors()
        if last_lon and last_lat:
            distanse = get_distance(source_lat, source_lon, my_lat, my_lon)
            print('Distance = ', distanse)
            if distanse < MAX_APPROVED_DISTANCE:
                if distanse > MAX_DISTANCE_MOVE:
                    # do move
                    distanse2 = get_distance(source_lat, source_lon, last_lat, last_lon)
                    A = [last_lat, last_lon]
                    B = [my_lat, my_lon]
                    C = [source_lat, source_lon]
                    direction = distanse <= distanse2
                    print('direction: ', direction)
                    D = calculate_direction(A, B, C)
                    left = 1
                    right = 1
                    if D == 0:
                        print('foreward')
                    else:
                        [angle2d, angle3d] = get_angle(A, B, C)
                        coof = 0
                        if angle3d > 90:
                            angle3d = 180 - angle3d
                        print('angle3d: ', angle3d)
                        angle = 90
                        if D < 0:
                            angle += angle3d
                            if not direction:
                                left = 0.3
                                right = 1
                        else:
                            angle -= angle3d
                            if not direction:
                                left = 1
                                right = 0.3
                        print('angle =', angle)
                        if direction:
                            angle /= -2
                            right = math.fabs(math.sin(angle * 3.14/180))
                            left = math.fabs(math.cos(angle * 3.14/180))
                        print("left :", left)
                        print("right :", right)
                    # a.runMotors([1, 4], round(right * 100))
                    # a.runMotors([2, 3], round(left * 100))
                else:
                    print('stop')
                    # a.stopMotors()
    time.sleep(2)


def testLocation():
    # import pudb; pudb.set_trace()
    global last_lat
    global last_lon
    global my_lat
    global my_lon
    global source_lat
    global source_lon
    locations = [
        [55.662329, 37.470107], #
        [55.662501, 37.470113], #
        [55.662667, 37.470180], # little right
        [55.662745, 37.470695], # right
        [55.662914, 37.470790], # left
        [55.662694, 37.470957], # backwards
    ]
    for l in locations:
        [last_lat, last_lon] = [my_lat, my_lon]
        [my_lat, my_lon] = [source_lat, source_lon]
        [source_lat, source_lon] = l
        print('last = ', [last_lat, last_lon])
        print('my = ', [my_lat, my_lon])
        print('source = ', [source_lat, source_lon])
        processLocation()
        print(' ')
        time.sleep(1)

# testLocation()
