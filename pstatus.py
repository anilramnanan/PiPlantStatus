import time
import grovepi
from grovepi import *
from grove_rgb_lcd import *
import socket
import fcntl
import struct
import tweepy

# Function gets the current IP address of the device
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])

# Sets a human readable status for soil moisture values
def soilStatus(value):
    if value == 0:
        soil_status = 'Sensor in open air'
    elif value >= 0 and value <= 300:
        soil_status = 'Dry'
    elif value > 300 and value <= 700:
        soil_status = 'Moist'
    elif value > 700:
        soil_status = 'Wet'
    else:
        soil_status = 'Sensor Error'
    return soil_status

# Sets a human readable status for the light values
def lightStatus(value):
    if value < 10:
	light_status = 'Dark'
    elif value >= 10 and value <=275:
	light_status = 'Dim'
    elif value > 275:
	light_status = 'Bright'
    else:
	light_status = 'Sensor Error'
    return light_status;		

# Define sensor ports
soil_sensor_port = 0
light_sensor_port = 1
dht_sensor_port = 5


photo_light_threshold = 275
light_value = 0
sStat = "N/A"
tStat = "N/A"
lStat = "N/A"

soil_error_status = 0
temp_error_status = 0
light_error_status = 0

# Twitter: Consumer keys and access tokens, used for OAuth
consumer_key = 'DHh0Gmkla9GKn3gtagBIAgjdk'
consumer_secret = 'lAM59VZdOfjVPtn4cNnZipWm8D29eY6uStysAYKjj4Hrzaucxn'
access_token = '3197751527-iIjcPx0FNTZoMw1CywGTYDJVV2Rwbg0U42OOWaL'
access_token_secret = 'KZGOVk7aGOgc3lLlXVbhA03260jJQsivLFbPdZd1G0RH1'

# Twitter: OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Twitter: Creation of the actual interface, using authentication
api = tweepy.API(auth)

# Grove: Check soil moisture sensor by reading analog signal. Report and error if nothing is found.
try:
	soil_moisture = grovepi.analogRead(soil_sensor_port)
	s = soilStatus(soil_moisture)
except (IOError) as e:
	soil_error_status = 1
	print soil_error_status

# Grove: Check light sensor by reading analog signal. Report and error if nothing is found.
try:
        light_value = grovepi.analogRead(light_sensor_port)
	l = lightStatus(light_value)
except (IOError) as e:
        light_error_status = 1
	print light_error_status

# Grove: Check temperature and humidity sensor by reading digital signal. Report and error if nothing is found.
try:
	[ temp,hum ] = dht(dht_sensor_port,0)           
	t = str(temp)
	h = str(hum)
	# setRGB(0,128,80)
	# setRGB(0,255,0)
	# setText("Temp:" + t + "C      " + "Humidity :" + h + "%")
	   
except (IOError,TypeError) as e:
        temp_error_status = 1
	print temp_error_status

# Display Temperature and Humidity on the LCD screen. Comment this out if you don't have one.
setRGB(0,128,80)
setRGB(0,255,0)
setText("Temp:" + t + "C      " + "Humidity :" + h + "%")


# Sent status messages if tehre are no errors from the sensors.
if temp_error_status != 1:
	tStat =  "Temp:" + t + "C      " + "Humidity :" + h + "%"

if soil_error_status != 1:
	sStat =  "Soil Moisture: " + s

if light_error_status !=1:
	lStat =  "Light Status: " + l; 


# Get IP address. This can be displayed on the LCD. Right now it is only used for debugging.
ipStat =  get_ip_address('wlan0')

# Create message to be tweeted from sensor status messages
msg = tStat + "\r\n" + sStat + "\r\n" + lStat

# If the light sensor detects there is enough light, tweet a photo along with the status.
 
if light_value > photo_light_threshold:
	print "Take a photo";
	api.update_with_media('/home/pi/GrovePi/PlantStatus/image.jpg',status= msg)
else:
	msg = msg + "\r\n" + "Too dark to take a photo"
	api.update_status(status = msg)

# Print message to console
print msg
