#!/usr/bin/python
import os
import sys
import time
import subprocess
import socketserver
import RPi.GPIO as GPIO

help = '''
Possible commands:
#cmd    device  off or on
light   <1-4>   <0,1>

#cmd    do
senseo  status  # Returns LED status
senseo  on-off  # Turns either on or off, same command for both
senseo  coffee  # Does a cup of coffee. If the Senseo is turned off, it turns on and waits till it preheats and does coffee.

#other
cmd     xbmc    status  # service xbmc status
cmd     xbmc    start   # service xbmc start
cmd     xbmc    stop    # service xbmc stop
cmd     temp            # Shows CPU temperature
cmd     hdd     sd      # Sends all "df -h" output of precoded devices
'''

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

'''Settings for Light-Switch'''
# Change the key[] variable below according to the dipswitches on your Elro receivers.
default_key = [0, 1, 1, 0, 1]
# Pin for 433MHz transmitter
default_pin = 10
# Number of transmissions
repeat = 10
# microseconds
pulselength = 300

'''Settings for Senseo'''
# On-Off Pin
power_pin = 11
# LED-Pin
led_pin = 13
# Pin for making coffee
coffee_pin = 15

GPIO.setup(led_pin, GPIO.IN)


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while 1:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            if not self.data:
                break
            client_data = self.data.decode('utf-8')
            client_words = client_data.split(' ')
            res = 'OK 200'

            # Light-Switch
            if client_words[0] == 'light':
                device = RemoteSwitch(device=int(client_words[1]),
                                      key=default_key,
                                      pin=default_pin)

                if int(client_words[2]):
                    device.switchOn()
                else:
                    device.switchOff()

            # Senseo
            elif client_words[0] == 'senseo':
                if client_words[1] == 'status':
                    res = self.senseo_status()
                elif client_words[1] == 'on-off':
                    self.senseo_on_off()
                elif client_words[1] == 'coffee':
                    self.senseo_coffee()

            # Other commands
            elif client_words[0] == 'cmd':
                if client_words[1] == 'xbmc':
                    if client_words[2] == 'status':
                        res = xbmc_status()
                    elif client_words[2] == 'start':
                        os.popen('service xbmc start')
                    elif client_words[2] == 'stop':
                        os.popen('service xbmc stop')
                elif client_words[1] == "temp":
                    res = 'CPU Temp: ' + os.popen('/opt/vc/bin/vcgencmd measure_temp').readline().replace("temp=", "").replace("'C\n", "") + ' °C'
                elif client_words[1] == "hdd":
                    if client_words[2] == "sd":
                        space = self.df('/dev/root')
                        res = '  SD: '
                        res += str(space[1:5]).replace(",", "").replace("'", "").replace("(", "").replace(")", "")
                # Other cmd's here

            else:
                res = 'Not all words could be found. ' + help

            self.request.sendall(res.encode('utf-8'))

    # Get Senseo status
    def senseo_status(self):
        return str(GPIO.input(13))

    # Turn Senseo on/off
    def senseo_on_off(self):
        try:
            GPIO.output(power_pin, 0)
        except RuntimeError:
            GPIO.setup(power_pin, GPIO.OUT)
        time.sleep(0.2)
        GPIO.output(power_pin, 1)

    # Make coffee
    def senseo_coffee(self):
        on = 0
        while not on:
            status_1 = GPIO.input(13)
            time.sleep(1.5)
            status_2 = GPIO.input(13)
            if status_1 and status_2:
                on = 1
                try:
                    GPIO.output(coffee_pin, 0)
                except RuntimeError:
                    GPIO.setup(coffee_pin, GPIO.OUT)
                time.sleep(0.2)
                GPIO.output(coffee_pin, 1)
            elif not status_1 and not status_2:
                self.senseo_on_off()
            else:
                time.sleep(10)

    # Get the status of the service xbmc
    def xbmc_status():
        status = subprocess.Popen(['service', 'xbmc', 'status'], stdout=subprocess.PIPE)
        output = status.communicate()[0]
        status = output.decode('utf-8')
        if status == 'xbmc stop/waiting\n':
            res = '0'
        else:
            res = '1'
        return res

    # Pretify "df -h"
    def df(self, filename):
        df = subprocess.Popen(["df", "-h", filename], stdout=subprocess.PIPE)
        output = df.communicate()[0]
        output = output.decode('utf-8')
        device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
        return device, size, used, available, percent, mountpoint


class RemoteSwitch(object):
    repeat = repeat
    pulselength = pulselength

    def __init__(self, device, key=[1, 1, 1, 1, 1], pin=11):
        self.pin = pin
        self.key = key
        self.device = device
        GPIO.setup(self.pin, GPIO.OUT)

    def switchOn(self):
        self._switch(GPIO.HIGH)

    def switchOff(self):
        self._switch(GPIO.LOW)

    def _switch(self, switch):
        self.bit = [142, 142, 142, 142, 142, 142, 142, 142, 142, 142, 142, 136, 128, 0, 0, 0]

        for t in range(5):
            if self.key[t]:
                self.bit[t] = 136
        x = 1
        for i in range(1, 6):
            if self.device & x > 0:
                self.bit[4 + i] = 136
            x = x << 1

        if switch == GPIO.HIGH:
            self.bit[10] = 136
            self.bit[11] = 142

        bangs = []
        for y in range(16):
            x = 128
            for i in range(1, 9):
                b = (self.bit[y] & x > 0) and GPIO.HIGH or GPIO.LOW
                bangs.append(b)
                x = x >> 1

        GPIO.output(self.pin, GPIO.LOW)
        for z in range(self.repeat):
            for b in bangs:
                GPIO.output(self.pin, b)
                time.sleep(self.pulselength / 1000000.)

if __name__ == "__main__":
    HOST, PORT = "", 54321
    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
