import json

from flask import Flask, url_for, send_from_directory, request
from flask import render_template

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
        l = 0
        r = 0
        direction = data.get('direction', '')
        if 'up' in direction:
            l += 1
            r += 1
        if 'down' in direction:
            l -= 1
            r -= 1
        if 'left' in direction:
            r += 1
        if 'right' in direction:
            l += 1
        if direction.strip() == '':
            l = 0
            r = 0
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
