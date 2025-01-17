from flask import Flask, render_template, jsonify, redirect, request, Response
import json
import database
import base64
from random import choice
from datetime import datetime
import person
import os
import binascii
from camera_pi import Camera

app = Flask(__name__)

logged_in = {}
api_loggers = {}
mydb = database.db('dbuser', '127.0.0.1', 'dbpass', 'ARMS')

global panServoAngle
global tiltServoAngle
panServoAngle = 90
tiltServoAngle = 90

panPin = 26
tiltPin = 19


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace;boundary=frame')

# this links to the main dashboard
@app.route("/", methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        user = person.user(request.form['username'], request.form['password'])
        if user.authenticated:
            user.session_id = str(binascii.b2a_hex(os.urandom(15)))
            logged_in[user.username] = {"object": user}
            return redirect('/overview/{}/{}'.format(request.form['username'], user.session_id))
        else:
            error = "invalid Username or Passowrd"

    return render_template('login.htm', error=error)

# this links is for device 1


@app.route('/device1/<string:username>/<string:session>', methods=["GET", "POST"])
def Dashoboard():
    user = {
        "username": "Aman Singh",
        "image": "static/images/amanSingh.jpg"
    }

    devices = [
        {"Dashboard": "device1",
         "deviceID": "Sensor_Pi"
         }
    ]
    return render_template('device_dashboard.htm', title='Dashobard', user=user, devices=devices)


@app.route('/overview/<string:username>/<string:session>', methods=['GET', 'POST'])
def overview(username, session):

    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username": username,
            "image": "/static/images/amanSingh.jpg",
            "api": logged_in[username]["object"].api,
            "session": session
        }

        devices = [
            {"Dashboard": "device1",
             "deviceID": "Sensor_Pi"
             }
        ]
        return render_template('overview.htm', title='Overview', user=user, devices=devices)

    else:
        return redirect('/')

# this location will get to the api setting


@app.route('/apisettings/<string:username>/<string:session>', methods=['GET', 'POST'])
def apisettings(username, session):

    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username": username,
            "image": "/static/images/amanSingh.jpg",
            "api": logged_in[username]["object"].api,
            "session": session
        }

        devices = [
            {"Dashboard": "device1",
             "deviceID": "Sensor_Pi"
             }
        ]
        return render_template('api_settings.htm', title='API-Settings', user=user, devices=devices)

    else:
        return redirect('/')


# this part is for the profile view
@app.route('/profile/<string:username>/<string:session>', methods=['GET', 'POST'])
def profile(username, session):

    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        user = {
            "username": username,
            "image": "/static/images/amanSingh.jpg",
            "api": logged_in[username]["object"].api,
            "session": session,
            "firstname": logged_in[username]["object"].first,
            "lastname": logged_in[username]["object"].last,
            "email": logged_in[username]["object"].email,
            "phone": logged_in[username]["object"].phone,
            "lastlogin": logged_in[username]["object"].last_login,
        }

        devices = [
            {"Dashboard": "device1",
             "deviceID": "Sensor_Pi"
             }
        ]
        return render_template('profile.htm', title='API-Settings', user=user, devices=devices)

    else:
        return redirect('/')

# this part is for the livestream view


@app.route('/livestream/<string:username>/<string:session>', methods=['GET', 'POST'])
def livestream(username, session,):
    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        templateData = {
            'panServoAngle': panServoAngle,
            'tiltServoAngle': tiltServoAngle
        }
        user = {
            "username": username,
            "image": "/static/images/amanSingh.jpg",
            "api": logged_in[username]["object"].api,
            "session": session,
        }
        return render_template('livestream.htm', title='Camera Livestream', templateData=templateData, user=user)
    else:
        return redirect('/')


@app.route('/livestream/<string:username>/<string:session>', methods=['POST'])
def my_form_post(username, session):
    global panServoAngle
    global tiltServoAngle
    if username in logged_in and (logged_in[username]['object'].session_id == session):
        panNewAngle = int(request.form['panServoAngle'])
        if (panNewAngle != panServoAngle):
            panServoAngle = panNewAngle
            os.system("python3 scripts/angleServoCtrl.py " +
                      str(panPin) + " " + str(panServoAngle))
        tiltNewAngle = int(request.form['tiltServoAngle'])
        if (tiltNewAngle != tiltServoAngle):
            tiltServoAngle = tiltNewAngle
            os.system("python3 scripts/angleServoCtrl.py " +
                      str(tiltPin) + " " + str(tiltServoAngle))
        user = {
            "username": username,
            "image": "/static/images/amanSingh.jpg",
            "api": logged_in[username]["object"].api,
            "session": session
        }
        templateData = {
            'panServoAngle': panServoAngle,
            'tiltServoAngle': tiltServoAngle
        }
        return render_template('livestream.htm', title='Camera Livestream', templateData=templateData, user=user)
    else:
        return redirect('/')


@app.route('/livestream/<string:username>/<string:session>/<servo>/<angle>', methods=['GET', 'POST'])
def move(username, session, servo, angle):
    global logged_in
    global panServoAngle
    global tiltServoAngle
    if username in logged_in and (logged_in[username]['object'].session_id == session):
        templateData = {
            'panServoAngle': panServoAngle,
            'tiltServoAngle': tiltServoAngle
        }
        user = {
            "username": username,
            "image": "/static/images/amanSingh.jpg",
            "api": logged_in[username]["object"].api,
            "session": session
        }
        if servo == 'pan':
            if angle == '+':
                panServoAngle = panServoAngle + 10
            else:
                panServoAngle = panServoAngle - 10
            os.system("python3.9 scripts/angleServoCtrl.py " +
                      str(panPin) + " " + str(panServoAngle))

        if servo == 'tilt':
            if angle == '+':
                tiltServoAngle = tiltServoAngle + 10
            else:
                tiltServoAngle = tiltServoAngle - 10
            os.system("python3.9 scripts/angleServoCtrl.py " +
                      str(tiltPin) + " " + str(tiltServoAngle))

        return render_template('livestream.htm', title='Camera Livestream', templateData=templateData, user=user)
    else:
        return redirect('/')


@app.route('/logout/<string:username>/<string:session>', methods=['GET', 'POST'])
def logout(username, session):

    global logged_in

    if username in logged_in and (logged_in[username]['object'].session_id == session):
        logged_in.pop(username)
        # print("logged out")
        return redirect('/')
    else:
        return redirect('/')

# this is the testing for api


@app.route("/api/<string:apikey>/test", methods=["GET", "POST"])
def apitest(apikey):
    return {"data": "working Fine Connected to the api server"}


# get all the devices information from the user
@app.route("/api/<string:apikey>/listdevices", methods=['GET', 'POST'])
def listdevices(apikey):
    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(
                apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            devices_list = apiuser.get_devices()
            api_loggers[apikey] = {"object": apiuser}
            return jsonify(devices_list)
        except Exception as e:
            print(e)
            return jsonify({"data": "Oops Looks like api is not correct"})

    else:
        data = api_loggers[apikey]["object"].get_devices()
        return jsonify(data)


randlist = [i for i in range(0, 100)]


@app.route('/api/<string:apikey>/deviceinfo/<string:deviceID>', methods=['GET', 'POST'])
def device_info(apikey, deviceID):
    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(
                apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            data = apiuser.dev_info(deviceID)
            api_loggers[apikey] = {"object": apiuser}
            # this part is hard coded so remove after fixing the issue
            data = list(data)
            data[2] = "Rosegarden"
            return jsonify(data)
        except Exception as e:
            print(e)
            return jsonify({"data": "Oops Looks like api is not correct"})

    else:
        data = api_loggers[apikey]["object"].dev_info(deviceID)

        # this part is hard coded so remove after fixing the issue
        print(data)
        data = list(data)
        data[2] = "Rosegarden"
        return jsonify(data)


@app.route('/api/<string:apikey>/fieldstat/<string:fieldname>', methods=['GET', 'POST'])
def fieldstat(apikey, fieldname):

    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(
                apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            data = apiuser.field_values(fieldname)
            api_loggers[apikey] = {"object": apiuser}
            return jsonify(data)
        except Exception as e:
            print(e)
            return jsonify({"data": "Oops Looks like api is not correct"})

    else:
        data = api_loggers[apikey]["object"].field_values(fieldname)
        return jsonify(data)


@app.route('/api/<string:apikey>/devicestat/<string:fieldname>/<string:deviceID>', methods=['GET', 'POST'])
def devicestat(apikey, fieldname, deviceID):

    global api_loggers
    global mydb
    if not(apikey in api_loggers):
        try:
            query = "select username from users where api_key = '{}'".format(
                apikey)
            mydb.cursor.execute(query)
            username = mydb.cursor.fetchall()
            username = username[0][0]
            apiuser = person.user(username, "dummy")
            apiuser.authenticated = True
            data = apiuser.device_values(fieldname, deviceID)
            api_loggers[apikey] = {"object": apiuser}
            return jsonify(data)
        except Exception as e:
            print(e)
            return jsonify({"data": "Oops Looks like api is not correct"})

    else:
        data = api_loggers[apikey]["object"].device_values(fieldname, deviceID)
        return jsonify(data)


@app.route('/api/<string:apikey>/update/<string:data>', methods=['GET', 'POST'])
def update_values(apikey, data):
    global mydb
    try:
        data = decode(data)
        output = mydb.get_apikeys()
        apikey = base64.b64decode(apikey).decode('ascii')
        if apikey in output:
            print("DATA ++")
            print(data)
            # print(data[3])

            if (len(data) == 6) and (type(data) is list):
                fieldname = data[0]
                deviceID = data[1]
                temp = data[2]
                moisture = data[3]
                humidity = data[4]
                light = data[5]
                mydb.update_values(apikey, fieldname, deviceID,
                                   temp, moisture, humidity, light)
                return ("Values Updated")
            else:
                return "Data Decoding Error!"
        else:
            return "Api key invalid"

    except Exception as e:
        print(e)
        return jsonify({"data": "Oops Looks like api is not correct"})


@app.route("/api/<string:apikey>/temperature", methods=["GET", "POST"])
def get_temperature(apikey):

    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)


@app.route("/api/<string:apikey>/moisture", methods=["GET", "POST"])
def get_moisture(apikey):
    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)


@app.route("/api/<string:apikey>/humidity", methods=["GET", "POST"])
def get_humidity(apikey):
    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)


@app.route("/api/<string:apikey>/light", methods=["GET", "POST"])
def get_light(apikey):
    randData = choice(randlist)
    time = datetime.now()
    time = time.strftime("%H:%M:%S")
    response = [time, randData]
    return jsonify(response)


def encode(data):
    data = json.dumps(data)
    message_bytes = data.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def decode(base64_message):
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return json.loads(message)


if __name__ == "__main__":
    # os.system("python3 scripts/Receiver_RPI.py &")
    app.run(host="0.0.0.0", port="8080", debug=True)
