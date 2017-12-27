import importlib 
import os
import socket
import subprocess
from flask import Flask, render_template, Response
from camera import Camera
import logging
from logging.handlers import RotatingFileHandler
app = Flask(__name__)


# keep runnign process global
proc = None

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

# Add streaming support
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=['GET', 'POST'])
def start_talkingraspi():
    global proc
    print(" > Start talkingraspi!")
    app.logger.info(' > Start Talkingraspi')
    proc = subprocess.Popen(["python", "/home/pi/RaspiSecurity/pi_surveillance.py", "-c", "/home/pi/RaspiSecurity/conf.json"])
    print(" > Process id {}".format(proc.pid))
    app.logger.info(" > Process id {}".format(proc.pid))
    return "Started!"


@app.route("/stop", methods=['GET', 'POST'])
def stop_talkingraspi():
    global proc
    print(" > Stop talkingraspi!")
    app.logger.info(' > Stop Talkingraspi')
    # subprocess.call(["kill", "-9", "%d" % proc.pid])
    proc.kill()
    print(" > Process {} killed!".format(proc.pid))
    if proc is None:
    	app.logger.info(" > Process {} killed!".format(proc.pid))
    return "Stopped!"


@app.route("/status", methods=['GET', 'POST'])
def status_talkingraspi():
    global proc
    if proc is None:
        print(" > Talkingraspi is resting")
    	app.logger.info(' > Talkingraspi is resting')
        return "Resting!"
    if proc.poll() is None:
        print(" > Talking raspi is running (Process {})!".format(proc.pid))
    	app.logger.info(" > Talking raspi is running (Process {})!".format(proc.pid))
        return "Running!"
    else:
        print(" > Talkingraspi is resting")
    	app.logger.info(' > Talkingraspi is resting')
        return "Stopped!"

# Add streaming support
@app.route("/video_feed")
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    handler = RotatingFileHandler('/tmp/foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.info("Connect to http://{}:5555 to controll TalkingRaspi !!".format(get_ip_address()))
    print("Connect to http://{}:5555 to controll TalkingRaspi!! defug = False, threaded=True".format(get_ip_address()))
    app.run(host="0.0.0.0", port=5555, debug=False, threaded=True)

