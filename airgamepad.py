from __future__ import print_function
import uinput
from uinput.ev import *
from select import select
from evdev import ecodes, InputDevice

air_kbd = "/dev/input/by-id/usb-SAGE_SAGE_AirMouse-event-kbd"
air_mouse = "/dev/input/by-id/usb-SAGE_SAGE_AirMouse-if01-event-mouse"

events = {
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
    ABS_X + (0, 1024, 0, 0),
    ABS_Y + (0, 1024, 0, 0)
}
keymap = {
    KEY_UP: BTN_SOUTH,
    KEY_DOWN: BTN_EAST,
    KEY_LEFT: BTN_NORTH,
    KEY_RIGHT: BTN_WEST,
    BTN_LEFT: BTN_TL,
    BTN_RIGHT: BTN_TR,
    KEY_PLAYPAUSE: BTN_SELECT,
    KEY_ENTER: BTN_START,
    KEY_ESC: BTN_MODE
}


def main():
    joy = uinput.Device(events,
                        name="Microsoft X-Box 360 pad",
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
                        joy.emit(keymap[k], ev.value)
                    elif k == KEY_VOLUMEUP:
                        joy.emit(ABS_Y, 0 if ev.value else 512)
                    elif k == KEY_VOLUMEDOWN:
                        joy.emit(ABS_Y, 1024 if ev.value else 512)
                    elif k == KEY_PREVIOUSSONG:
                        joy.emit(ABS_X, 0 if ev.value else 512)
                    elif k == KEY_NEXTSONG:
                        joy.emit(ABS_X, 1024 if ev.value else 512)


main()
