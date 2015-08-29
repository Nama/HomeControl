#!/usr/bin/python
import os
import sys
import socket
import time
from PIL import Image
from lglcd import LogitechLcd
from threading import Thread


def load_image(sprite):
    im = Image.open(sprite)
    im = im.convert('1')
    return list(im.getdata())


def background(sprite):
    lcd.set_background(load_image(sprite))
    lcd.update()


def exit():
    s.close()
    os._exit(0)


def status(e):
    while process_status.is_alive:
        if process_status_work:
            s.send(b'senseo status')
            data = s.recv(buffer_size)
            status = int(data.decode('utf-8'))
            if status:
                background(sprite_on)
            else:
                background(sprite_off)
            time.sleep(1.5)


def button_pressed(button, short_press):
    global mode
    if button == 1:
        if short_press:
            if mode == 'senseo':
                s.send(b'senseo on-off')
                data = s.recv(buffer_size)
            else:
                s.send(b'light 1 0')
                data = s.recv(buffer_size)
                exit()
        else:
            if mode == 'lights':
                s.send(b'light 1 1')
                data = s.recv(buffer_size)
                exit()
    elif button == 2:
        if short_press:
            if mode == 'senseo':
                global process_status_work
                process_status_work = False
                s.send(b'senseo coffee')
                background(sprite_heating)
                data = s.recv(buffer_size)
                for i in range(60):
                    background(sprite_coffe1)
                    time.sleep(0.3)
                    background(sprite_coffe2)
                    time.sleep(0.3)
                background(sprite_coffe3)
                time.sleep(10)
                process_status_work = True
            else:
                s.send(b'light 2 0')
                data = s.recv(buffer_size)
                exit()
        else:
            if mode == 'lights':
                s.send(b'light 2 1')
                data = s.recv(buffer_size)
                exit()
    elif button == 4:
        if short_press:
            if mode == 'senseo':
                process_status_work = False
                mode = 'lights'
                background(sprite_lights)
            else:
                s.send(b'light 3 0')
                data = s.recv(buffer_size)
                exit()
        else:
            if mode == 'lights':
                s.send(b'light 3 1')
                data = s.recv(buffer_size)
                exit()
    elif button == 8:
        if short_press:
            if mode == 'senseo':
                exit()
            else:
                s.send(b'light 4 0')
                data = s.recv(buffer_size)
                exit()
        else:
            if mode == 'lights':
                s.send(b'light 4 1')
                data = s.recv(buffer_size)
                exit()


def buttons(button):
    while process_buttons.is_alive:
        time.sleep(0.001)
        if lcd.is_button_pressed(button):
            pressed = time.time()
            while lcd.is_button_pressed(button):
                time.sleep(0.001)
                pressed_time = int((time.time() - pressed) * 1000)
                if pressed_time < 350:
                    short_press = True
                else:
                    short_press = False
            button_pressed(button, short_press)

if __name__ == "__main__":
    lcd = LogitechLcd('HomeControl Client')
    sprite_init = 'init.png'
    sprite_on = 'on.png'
    sprite_off = 'off.png'
    sprite_heating = 'preheating.png'
    sprite_lights = 'lights.png'
    sprite_coffe1 = 'coffee1.png'
    sprite_coffe2 = 'coffee2.png'
    sprite_coffe3 = 'coffee3.png'
    global mode
    mode = 'senseo'

    # Set initialization image,
    # till connection ist established and status-thread is running
    background(sprite_init)

    # Socket-Server
    ip = 'senseo'
    port = 54321
    buffer_size = 1024
    display_time = 300

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    # Start threads for status and buttons
    process_status_work = True
    process_status = Thread(target=status, args=('yorp', ))
    process_status.start()
    for button in 1, 2, 4, 8:
        process_buttons = Thread(target=buttons, args=(button, ))
        process_buttons.start()
