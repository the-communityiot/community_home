import jsonconverter as jsonc
import dynamodb
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
app = Flask(__name__)
app.secret_key = 'specialsecretkey'

# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    session.pop('email', None)
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        pwd = dynamodb.getlogin(email, password)[0]
        identifier = dynamodb.getlogin(email, password)[1]
        if(pwd == password):
            session['email'] = identifier
            return redirect(url_for('index'))

        else:
            return redirect(url_for('login'))
    return render_template('login.html')

# Adding user
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'username' in request.form:
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        dynamodb.registeruser(email, username, password)
        return redirect(url_for('index'))

# Adding license
@app.route("/addlicense", methods=['GET', 'POST'])
def addlicense():
    if request.method == 'POST' and 'licensenumber' in request.form:
        licensenumber = request.form['licensenumber']
        dynamodb.addlicenseplate(licensenumber)
        return redirect(url_for('index'))

# Deleting user
@app.route("/deleteuser", methods=['GET', 'POST'])
def deleteuser():
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        dynamodb.deleteuser(email)
        return redirect(url_for('index'))

# Deleting license
@app.route("/deletelicense", methods=['GET', 'POST'])
def deletelicense():
    if request.method == 'POST' and 'licensenumber' in request.form:
        licensenumber = request.form['licensenumber']
        dynamodb.deletelicenseplate(licensenumber)
        return redirect(url_for('index'))

# Get NightDay status
@app.route("/getNightDay", methods=['POST', 'GET'])
def getNightDay():
    data = {'mode': dynamodb.get_data_light_night()}
    return jsonify(data)

# Get Temperature data
@app.route("/api/getdata", methods=['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodb.get_data_from_dynamodb_temperature()),
                    'title': "IOT Data"}
            return jsonify(data)

        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

# Get one Temperature data
@app.route("/api/getdataone", methods=['POST', 'GET'])
def apidata_getdataone():
    temphum = dynamodb.get_data_from_dynamodb_temperatureone()
    temphum1 = temphum[0]
    print(type(temphum))
    temphumdata = {'temperature': str(temphum1["temperature"]),
                'humidity': str(temphum1["humidity"])}

    return jsonify(temphumdata)

# Get Users data
@app.route("/api/getusers", methods=['POST', 'GET'])
def apidata_getusers():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'users_chart': jsonc.data_to_json(dynamodb.get_data_from_dynamodb_users()),
                    'title': "Users Data"}
            return jsonify(data)
        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

# Get Light data
@app.route("/api/getlightdata", methods=['POST', 'GET'])
def apidata_getlightdata():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'light_chart': jsonc.data_to_json(dynamodb.get_data_from_dynamodb_Light()),
                    'title': "Light Data"}
            return jsonify(data)
        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

# Get License data
@app.route("/api/getlicensedata", methods=['POST', 'GET'])
def apidata_getlicensedata():
    if request.method == 'POST' or request.method == 'GET':
        try:
            data = {'license_chart': jsonc.data_to_json(dynamodb.get_data_from_dynamodb_license()),
                    'title': "License Data"}
            return jsonify(data)
        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

# Log out
@app.route("/backout")
def backout():
    session.pop('email', None)
    return render_template("login.html")

# Index page
@app.route("/index")
def index():
    if 'email' in session:
        return render_template("index.html")
    else:
        return redirect(url_for("login"))

# Lights dashboard
@app.route("/lights")
def lights():
    if 'email' in session:
        return render_template('lights.html')
    else:
        return redirect(url_for("login"))

# Temperature dashboard
@app.route("/temperature")
def temperature():
    if 'email' in session:
        return render_template('temperature.html')
    else:
        return redirect(url_for("login"))

# Register user page
@app.route("/registerRedirect")
def registerRedirect():
    if 'email' in session:
        return render_template('register.html')
    else:
        return redirect(url_for("login"))

# Add license page
@app.route("/addlicenseRedirect")
def addlicenseRedirect():
    if 'email' in session:
        return render_template('addlicense.html')
    else:
        return redirect(url_for("login"))

# Delete user page
@app.route("/deleteuserRedirect")
def deleteuserRedirect():
    if 'email' in session:
        return render_template('deleteuser.html')
    else:
        return redirect(url_for("login"))

# Delete license page
@app.route("/deletelicenseRedirect")
def deletelicenseRedirect():
    if 'email' in session:
        return render_template('deletelicense.html')
    else:
        return redirect(url_for("login"))

# Control LED
@app.route("/writeLED/<status>")
def writePin(status):
    
    host = "ajv7uofdulvct-ats.iot.us-east-1.amazonaws.com"
    rootCAPath = "rootca.pem"
    certificatePath = "certificate.pem.crt"
    privateKeyPath = "private.pem.key"

    my_rpi = AWSIoTMQTTClient("p1828175-basicPubSub2")
    my_rpi.configureEndpoint(host, 8883)
    my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
    my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
    my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

    my_rpi.connect()
    my_rpi.publish("led/lightcontrol", status, 1)
    response = status
    return response

# Control Door
@app.route("/writeDoor/<status1>")
def writeDoors(status1):

    host = "ajv7uofdulvct-ats.iot.us-east-1.amazonaws.com"
    rootCAPath = "rootca.pem"
    certificatePath = "certificate.pem.crt"
    privateKeyPath = "private.pem.key"

    my_rpi = AWSIoTMQTTClient("p1828175-basicPubSub2")
    my_rpi.configureEndpoint(host, 8883)
    my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
    my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
    my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

    my_rpi.connect()
    my_rpi.publish("led/doorcontrol", status1, 1)
    response = status1
    return response

app.run(debug=True, port=8001, host="0.0.0.0")
