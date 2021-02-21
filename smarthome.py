# The Community Smart Home
# Made by Keith Chan, Nicholas Chong, Kenneth Kuah
# Class : DISM/FT/3A/41

# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from rpi_lcd import LCD
from time import sleep
from time import time
import random
import Adafruit_DHT
import sys
import telepot
from gpiozero import Buzzer
from gpiozero import MotionSensor
from gpiozero import LED
from gpiozero import MCP3008
from picamera import PiCamera
import boto3
import botocore
import RPi.GPIO as GPIO
from multiprocessing import Process
import threading
import datetime as datetime
import json
import time

# Initalize Hardware

# DHT11 Sensor  :   GPIO PIN 20
# Motion Sensor :   GPIO PIN 26
# Lights LED    :   GPIO PIN 21
# Door LED      :   GPIO PIN 16
# Buzzer        :   GPIO PIN 5
# Servo Motor   :   GPIO PIN 12
# Keypad        :   GPIO PIN 19, 17, 27, 22, 18, 23, 24, 25

sens1 = 20
adc = MCP3008(channel=0)
light = round(1024-(adc.value*1024))
pir = MotionSensor(26, sample_rate=5, queue_len=1)
led = LED(21)
doorled = LED(16)
LCD = LCD()
bz = Buzzer(5)
passcode = '12345'

# Initalize Servo
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
servo1 = GPIO.PWM(12, 50)
servo1.start(0)
servo1.ChangeDutyCycle(2)

# Numpad Matrix
MATRIX = [[1,2,3,'A'],
		  [4,5,6,'B'],
		  [7,8,9,'C'],
		  ['*',0,'#','D']]

# Match pins to rows and columns
ROW = [19,17,27,22]
COL = [18,23,24,25]

# Create an S3 resource
s3 = boto3.resource('s3')
BUCKET = 'p1828175-s3-bucket'
location = {'LocationConstraint': 'us-east-1'}
file_path = '/home/pi/Desktop/pic'

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")

# Custom MQTT command to turn on/off lights
def customCallbacklight(client, userdata, message):
    if message.payload == 'On':
        ledOn()
    else:
        ledOff()

# Custom MQTT command to open/close door
def customCallbackdoor(client, userdata, message):
    if message.payload == 'Open':
        led2On()
    else:
        led2Off()

# Telegram bot
my_bot_token = '1438876586:AAEs9xchqrhMo2BeZZn06LeNDZhqXzb592k'
chat_id = '172867422'

host = "ajv7uofdulvct-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "rootca.pem"
certificatePath = "certificate.pem.crt"
privateKeyPath = "private.pem.key"

# Configure MQTT Client
my_rpi = AWSIoTMQTTClient("p1828175-basicPubSub")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT

# "sensors/DHT" is for publishing DHT temperature and humidity values to DynamoDB
# "sensors/light" is for publishing Light values to DynamoDB
# "mode/daynight" is for changing the day night mode.
# "led/lightcontrol" is for controlling the lights
# "led/doorcontrol" is for controlling the door

my_rpi.connect()
my_rpi.subscribe("sensors/DHT", 1, customCallback)
my_rpi.subscribe("sensors/light", 1, customCallback)
my_rpi.subscribe("mode/daynight", 1, customCallback)
my_rpi.subscribe("led/lightcontrol", 1, customCallbacklight)
my_rpi.subscribe("led/doorcontrol", 1, customCallbackdoor)
sleep(2)

# Open garage door
def openGarage():
    GPIO.output(12, True)
    servo1.ChangeDutyCycle(6)
    sleep(10)
    GPIO.output(12, True)
    servo1.ChangeDutyCycle(2)
    sleep(2)
    GPIO.output(12, False)
    servo1.ChangeDutyCycle(0)

# For toggle lights
def ledOn():
    led.on()
    return "On"

def ledOff():
    led.off()
    return "Off"

# For toggle door (LED)
def led2On():
    doorled.on()
    return "Open"

def led2Off():
    doorled.off()
    return "Close"

# Open door
def openDoor():
    doorled.on()
    sleep(5)
    doorled.off()

# Telegram respond msg

# If humidity levels is greater than 60, chances of rain are high
# If humidity levels is lesser than 60, chances of rain are low

# If brightness levels is greater than 800, it is sunny
# If brightness levels is greater than 500 but lesser than 800, it is cloudy
# If brightness levels is lesser than 500, it is dark

# If passcode is given in message, open door
# If /open_garage_door is given in message, open garage door

def respondToMsg(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print('Got command: {}'.format(command))
    if command == '/temperature_value':
        temperature, humidity = getTempHum()
        bot.sendMessage(chat_id, 'The temperature is {} C'.format(temperature))    
    elif command == '/humidity_value':
        temperature, humidity = getTempHum()
        if humidity > 60.0:
            bot.sendMessage(chat_id, 'The humidity is {}, chances of rain are high'.format(humidity))
        else:
            bot.sendMessage(chat_id, 'The humidity is {}, chances of rain are low'.format(humidity))
    elif command == '/brightness_value':
        brightness = getLight()
        if brightness > 800.0:
            bot.sendMessage(chat_id, 'The brightness level is {}, it is sunny!'.format(brightness))
        elif brightness in range(500,799):
            bot.sendMessage(chat_id, 'The brightness level is {}, it is cloudy!'.format(brightness))
        elif brightness < 500:
            bot.sendMessage(chat_id, 'The brightness level is {}, it is dark!'.format(brightness))
    elif command == '/open_main_door':
        bot.sendMessage(chat_id, 'Enter password:')
    elif command == '12345':
        bot.sendMessage(chat_id, 'Door opened')
        doorled.on()
        sleep(5)
        doorled.off()
    elif command == '/open_garage_door':
        bot.sendMessage(chat_id, 'Garage door opened for 10 Seconds')
        openGarage()
    else:
        bot.sendMessage(chat_id, 'Enter again')

# Get value functions
def getTempHum():
    humidity, temperature = Adafruit_DHT.read_retry(11, sens1)
    return temperature, humidity

def getLight():
    light = round(1024-(adc.value*1024))
    return light

def getDatetime():
    now = datetime.datetime.now()
    return now

# Publish values to AWS DynamoDB
def publishTempHum():
    while True:
        temperature, humidity = getTempHum()
        message = {}
        message["tempid"] = "tempid_community"
        now = getDatetime()
        message["datetimeid"] = now.isoformat()
        message["temperature"] = temperature
        message["humidity"] = humidity
        my_rpi.publish("sensors/DHT", json.dumps(message), 1)
        sleep(10)

def publishLight():
    while True:
        light = getLight()
        message = {}
        message["lightid"] = "lightid_community"
        now = getDatetime()
        message["datetimeid"] = now.isoformat()      
        message["lightvalue"] = light
        my_rpi.publish("sensors/light", json.dumps(message), 1)
        sleep(10)

def publishMode(mode):
    message = {}
    message["DayNightID"] = "daynight_community"
    message["mode"] = mode
    my_rpi.publish("mode/daynight", json.dumps(message), 1)

# Day Mode
def lightLED():
    while True:
        light = getLight()
        if light < 800.0:
            led.on()
        else:
            led.off()
        sleep(5)

# LCD screen options menu
def options_menu():
    LCD.text('A:NightM B:Door',1)
    LCD.text('C:TemHum D:GDoor',2)

# Camera take photo
def takePhoto(file_path,file_name):
    with PiCamera() as camera:
        # camera.resolution = (1024, 768)
        full_path = file_path + "/" + file_name
        camera.capture(full_path)

# Upload to S3
def uploadToS3(file_path,file_name, bucket_name,location):
    s3 = boto3.resource('s3') # Create an S3 resource
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    if exists == False:
        s3.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    # Upload the file
    full_path = file_path + "/" + file_name
    s3.Object(bucket_name, file_name).put(Body=open(full_path, 'rb'))
    print("File uploaded")

# AWS Rekognition for text (License Plate Reader)
def detect_text(file_name, bucket, region="us-east-1"):
    client=boto3.client('rekognition', region)
    response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':file_name}})              
    textDetections=response['TextDetections']
    print ('Detected text\n----------')
    licensePlate = get_data_from_dynamodb()
    for text in textDetections:
        for License in licensePlate:
            if(text['DetectedText'] == License['license']):
                print ('Detected text:' + text['DetectedText'])
                print('License plate {license} detected'.format(license=License))
                print ('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
                bot.sendMessage(chat_id, "Car recognised, opening garage door! A photo will be sent.")
                bot.sendPhoto(chat_id, photo = open(file_path + '/' + file_name, 'rb'))
                openGarage()
                return len(textDetections)

# Get data from DynamoDB
def get_data_from_dynamodb():
    try:
        import boto3
        from boto3.dynamodb.conditions import Key, Attr

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('licensedata')

        resp = table.scan(AttributesToGet=['license'])

        return resp['Items']

    except:
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

# Motion Sensor
def senseMotion():
    while True:
        i = GPIO.input(26)
        if i == 1:
            print("Motion detected!")
            print("Taking Photo of License Plate")
            timestring = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            file_name = 'photo_'+timestring+'.jpg'
            takePhoto(file_path,file_name)
            print("Uploading to S3")
            uploadToS3(file_path,file_name, BUCKET,location)
            print("Detecting License Plate")
            text_count=detect_text(file_name,BUCKET)
            print("Text detected: " + str(text_count))
            sleep(1)

# Function for when user enters correct password
def correct_pass():
    bz.on()
    sleep(1)
    bz.off()
    print "success"
    bot.sendMessage(chat_id, "Correct password, main door opened.")
    LCD.text('Welcome to the', 1)
    LCD.text('Community!', 2)
    sleep(5)
    options_menu()
    NightBool = False
    mode='Day Mode'
    publishMode(mode)
    p = proc_start()
    while(True):
        for j in range(4):
            GPIO.output(COL[j],0)
            for i in range(4):
                if GPIO.input(ROW[i]) == 0:
                    if MATRIX[i][j] == "A":
                        if NightBool == True:
                            LCD.text('Day Mode',1)
                            LCD.text('Activated',2)
                            p = proc_start()
                            sleep(3)
                            options_menu()
                            NightBool = False
                            mode='Day Mode'
                            publishMode(mode)
                        else:
                            LCD.text('Night Mode',1)
                            LCD.text('Activated',2)
                            proc_stop(p)
                            if GPIO.input(21) == 1:
                                led.off()
                            sleep(3)
                            options_menu()
                            NightBool = True
                            mode='Night Mode'
                            publishMode(mode)
                    elif MATRIX[i][j] == "B":
                        bot.sendMessage(chat_id, 'Main Door opened')
                        LCD.text('Door',1)
                        LCD.text('Opening',2)
                        doorled.on()
                        sleep(10)
                        doorled.off()
                        options_menu()
                    elif MATRIX[i][j] == "C":
                        temperature, humidity = getTempHum()
                        LCD.text('Temperature:{:.1f}'.format(temperature),1)
                        LCD.text('Humidity:{:.1f}'.format(humidity),2)
                        sleep(7)
                        options_menu()
                    elif MATRIX[i][j] == "D":
                        bot.sendMessage(chat_id, 'Garage door opened for 10 Seconds')
                        LCD.text('Garage Door',1)
                        LCD.text('Opening',2)
                        openGarage()
                        options_menu()
            GPIO.output(COL[j],1)

# Function for when the user enters wrong password
def wrong_pass(passwordCounter):
    bz.on()
    sleep(0.1)
    bz.off()
    sleep(0.1)
    bz.on()
    sleep(0.1)
    bz.off()
    print "failed"
    LCD.text('Wrong Password!', 1)
    passwordCounter+=1
    countdown = 10
    LCD.text('', 2)
    if passwordCounter == 3:
        bot.sendMessage(chat_id, "Password keyed in wrong 3 times! Lock disabled for 10 Seconds.")
        while countdown != 0:
            LCD.text('Disabled for:{}'.format(countdown), 1)
            countdown = countdown - 1
            sleep(1)
        passwordCounter = 0
    sleep(3)
    return passwordCounter

# Function for detecting the password
def button_sens():
    global passEnter
    global passwordCounter
    global passEnterDisplay
    passwordCounter = 0
    while(True):
        for j in range(4):
            GPIO.output(COL[j],0)
            for i in range(4):
                if GPIO.input(ROW[i]) == 0:
                    bz.on()
                    print MATRIX[i][j]
                    sleep(0.2)
                    bz.off()
                    if MATRIX[i][j] == "A":
                        passEnter = passEnter[0:len(passEnter)-1:]
                        passEnterDisplay = passEnterDisplay[0:len(passEnterDisplay)-1:]
                        LCD.text(passEnterDisplay,2)
                        sleep(0.2)
                    else:
                        passEnter = passEnter + str(MATRIX[i][j])
                        passEnterDisplay = passEnterDisplay + str(MATRIX[i][j])
                        if len(passEnterDisplay) > 1:
                            passEnterDisplay_list = list(passEnterDisplay)
                            passEnterDisplay_list[len(passEnterDisplay)-2] = "*"
                            passEnterDisplay = "".join(passEnterDisplay_list)
                        LCD.text(passEnterDisplay,2)
                        if passEnter == passcode and len(passEnter) == 5:
                            correct_pass()
                            passEnter=''
                            passEnterDisplay = ''
                            LCD.text('Password: ', 1)
                        elif passEnter != passcode and len(passEnter) == 5:
                            passwordCounter = wrong_pass(passwordCounter)
                            passEnter=''
                            passEnterDisplay=''
                            LCD.text('Password: ', 1)
                        while (GPIO.input(ROW[i]) == 0):
                            pass
            GPIO.output(COL[j],1)

# Start Day mode
def proc_start():
    t5 = Process(target=lightLED)
    t5.start()
    return t5

# Off Day mode
def proc_stop(p_to_stop):
    p_to_stop.terminate()

for j in range(4):
	GPIO.setup(COL[j], GPIO.OUT)
	GPIO.output(COL[j], 1)

for i in range(4):
	GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

bot = telepot.Bot(my_bot_token)
bot.message_loop(respondToMsg)

try:
    LCD.text('Password: ', 1)
    passEnter=''
    passEnterDisplay=''
    t1 = threading.Thread(target=publishTempHum) 
    t2 = threading.Thread(target=publishLight)
    t3 = threading.Thread(target=senseMotion)
    t4 = threading.Thread(target=button_sens)
    # starting thread 1 
    t1.start()
    # starting thread 2
    t2.start()
    # starting thread 3
    t3.start()
    # starting thread 4
    t4.start()

except (KeyboardInterrupt,SystemExit):
    LCD.text('Program Quit', 1)
    LCD.text('', 2)
    GPIO.cleaup()