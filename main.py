import libevdev
import json
import time
import RPi.GPIO as GPIO

config = json.load(open('config.json'))
DO_SEND_KEYS = True # set to False for debugging

def create_device():
    device = libevdev.Device()
    device.name = config['device_name']

    keymap = config['keymap']

    row_length = len(keymap[0])
    for r, row in enumerate(keymap):
        if len(row) != row_length:
            raise ValueError(f'All rows must have the same length (row {r})')
        for c, key in enumerate(row):
            keymap[r][c] = libevdev.evbit(key)
            device.enable(keymap[r][c])

    uinput = device.create_uinput_device()
    print(f'Created device {uinput.devnode}')
    return uinput, keymap

def setup_pins():
    GPIO.setmode(GPIO.BCM)
    for row_pin in config['keyboard_row_pins']:
        GPIO.setup(row_pin, GPIO.IN, GPIO.PUD_DOWN)

    for col_pin in config['keyboard_col_pins']:
        GPIO.setup(col_pin, GPIO.OUT)
        GPIO.output(col_pin, GPIO.LOW)

def test_col(col_pin, row_pins):
    result = []
    GPIO.output(col_pin, GPIO.HIGH)
    time.sleep(config['col_set_delay_ms']/1000)
    for row_pin in row_pins:
        time.sleep(config['key_read_delay_ms']/1000)
        result.append(GPIO.input(row_pin))
    GPIO.output(col_pin, GPIO.LOW)
    return result

def main():
    setup_pins()
    if DO_SEND_KEYS:
        uinput, keymap = create_device()
    old_state = [[False for _ in config['keyboard_col_pins']] for _ in config['keyboard_row_pins']]
    last_start = time.time()
    while True:
        for c, col_pin in enumerate(config['keyboard_col_pins']):
            key_states = test_col(col_pin, config['keyboard_row_pins'])
            for r, state in enumerate(key_states):
                if state == old_state[r][c]:
                    continue
                if state:
                    print(f'Pressed {r}, {c} (key {config["keymap"][r][c]})')
                    if DO_SEND_KEYS:
                        events = [libevdev.InputEvent(keymap[r][c], 1), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                        uinput.send_events(events)
                else:
                    print(f'Released {r}, {c} (key {config["keymap"][r][c]})')
                    if DO_SEND_KEYS:
                        events = [libevdev.InputEvent(keymap[r][c], 0), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                        uinput.send_events(events)
                old_state[r][c] = state
        time_elapsed = time.time() - last_start
        time.sleep(max(1/config['scanning_frequency']-time_elapsed,0))
        last_start = time.time()
    
if __name__ == '__main__':
    main()
