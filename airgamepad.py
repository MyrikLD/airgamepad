from __future__ import print_function
import uinput
from uinput.ev import *
from sys import argv, exit
from select import select
from evdev import ecodes, InputDevice, list_devices, AbsInfo, events
from enum import Enum

air_kbd = "/dev/input/by-id/usb-SAGE_SAGE_AirMouse-event-kbd"
air_mouse = "/dev/input/by-id/usb-SAGE_SAGE_AirMouse-if01-event-mouse"

evfmt = '{} ({:<4}), {}'

def print_event(e):
    if e.type != ecodes.EV_SYN:
        if e.type in ecodes.bytype:
            codename = ecodes.bytype[e.type][e.code]
        else:
            codename = '?'

        print(evfmt.format(codename, e.code, e.value))


device_mouse = InputDevice(air_mouse)
device_kbd = InputDevice(air_kbd)

def print_capabs(dev):
    capabs = dev.capabilities(verbose=True)
    print('Device capabilities:')
    for type, codes in capabs.items():
        print('  Type {} {}:'.format(*type))
        for i in codes:
            if isinstance(i[1], AbsInfo):
                print('    Code {:<4} {}:'.format(*i[0]))
                print('      {}'.format(i[1]))
            else:
                # multiple names may resolve to one value
                s = ', '.join(i[0]) if isinstance(i[0], list) else i[0]
                print('    Code {:<4} {}'.format(s, i[1]))
        print('')

def main():
    """
        Event type 1 (EV_KEY)
            Event code 304 (BTN_SOUTH)
            Event code 305 (BTN_EAST)
            Event code 307 (BTN_NORTH)
            Event code 308 (BTN_WEST)
            Event code 310 (BTN_TL)
            Event code 311 (BTN_TR)
            Event code 314 (BTN_SELECT)
            Event code 315 (BTN_START)
            Event code 316 (BTN_MODE)
            Event code 317 (BTN_THUMBL)
            Event code 318 (BTN_THUMBR)
    """
    evs = {
        BTN_SOUTH,
        BTN_EAST,
        BTN_NORTH,
        BTN_WEST,
        BTN_TL,
        BTN_TR,
        BTN_SELECT,
        BTN_START,
        BTN_MODE,
        BTN_THUMBL,
        BTN_THUMBR,
        ABS_X+(0, 1024, 0, 0),
        ABS_Y+(0, 1024, 0, 0)
    }
    keymap = {
        KEY_UP: BTN_SOUTH,
        KEY_DOWN: BTN_EAST,
        KEY_LEFT: BTN_NORTH,
        KEY_RIGHT: BTN_WEST,
        (1, 272):BTN_TL,
        BTN_RIGHT:BTN_TR,
        KEY_PLAYPAUSE:BTN_SELECT,
        KEY_ENTER:BTN_START,
        KEY_ESC:BTN_MODE
    }
    joy = uinput.Device(evs,
                        name="My Microsoft X-Box 360 pad",
                        bustype=0x03,
                        vendor=0x45e,
                        product=0x28e,
                        version=0x110
                        )
    joy.emit(ABS_X, 512)
    joy.emit(ABS_Y, 512)
    devices = map(InputDevice, (air_kbd, air_mouse))
    devices = {dev.fd: dev for dev in devices}
    for d in devices.values():
        d.grab()

    print('Listening for events ...\n')
    while True:
        r, w, e = select(devices, [], [])

        for d in r:
            for ev in devices[d].read():
                if ev.type == ecodes.EV_KEY and ev.value != 2:
                    k = (ev.type, ev.code)
                    if k in keymap.keys():
                        if ev.value == 1:
                            joy.emit(keymap[k], ev.value)
                        else:
                            joy.emit(keymap[k], ev.value)
                    if k == KEY_VOLUMEUP:
                        if ev.value == 1:
                            joy.emit(ABS_Y, 0)
                        else:
                            joy.emit(ABS_Y, 512)
                    if k == KEY_VOLUMEDOWN:
                        if ev.value == 1:
                            joy.emit(ABS_Y, 1024)
                        else:
                            joy.emit(ABS_Y, 512)
                    if k == KEY_PREVIOUSSONG:
                        if ev.value == 1:
                            joy.emit(ABS_X, 0)
                        else:
                            joy.emit(ABS_X, 512)
                    if k == KEY_NEXTSONG:
                        if ev.value == 1:
                            joy.emit(ABS_X, 1024)
                        else:
                            joy.emit(ABS_X, 512)

main()