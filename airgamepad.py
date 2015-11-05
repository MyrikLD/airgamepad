from __future__ import print_function
import uinput
from uinput.ev import *
from select import select
from evdev import ecodes, InputDevice, AbsInfo

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
        ABS_X + (0, 1024, 0, 0),
        ABS_Y + (0, 1024, 0, 0)
    }
    keymap = {
        KEY_UP: BTN_SOUTH,
        KEY_DOWN: BTN_EAST,
        KEY_LEFT: BTN_NORTH,
        KEY_RIGHT: BTN_WEST,
        (1, 272): BTN_TL,
        BTN_RIGHT: BTN_TR,
        KEY_PLAYPAUSE: BTN_SELECT,
        KEY_ENTER: BTN_START,
        KEY_ESC: BTN_MODE
    }
    joy = uinput.Device(evs,
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
