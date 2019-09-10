import numpy as np

import cv2
from flask import Flask, render_template, request
from flask_cors import CORS
from py_flask_movie.flask_movie import FlaskMovie
from py_pipe.pipe import Pipe

app = Flask(__name__)
CORS(app)

flask_movie = FlaskMovie(app)

color_pipe = Pipe(limit=1)
mask_pipe = Pipe(limit=1)
filter_pipe = Pipe(limit=1)

flask_movie.create('color_feed', color_pipe)
flask_movie.create('mask_feed', mask_pipe)
flask_movie.create('filter_feed', filter_pipe)

lower_hsv = [30, 150, 50]
upper_hsv = [255, 255, 180]


@app.route('/')
def index_html():
    return render_template('index.html')


@app.route('/update', methods=['POST', 'GET'])
def controls():
    global lower_hsv, upper_hsv
    lower_hsv = list(map(int, [request.args.get('lh'), request.args.get('ls'), request.args.get('lv')]))
    upper_hsv = list(map(int, [request.args.get('uh'), request.args.get('us'), request.args.get('uv')]))
    print(lower_hsv, upper_hsv)
    return request.query_string


cap = cv2.VideoCapture(0)
flask_movie.start(bind_ip='0.0.0.0', bind_port=5000)

while True:
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array(lower_hsv)
    upper_red = np.array(upper_hsv)

    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    color_pipe.push(frame)
    mask_pipe.push(mask)
    filter_pipe.push(res)

    cv2.waitKey(1)
