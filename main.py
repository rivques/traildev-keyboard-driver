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
    fn_keymap = config['fn_keymap']

    row_length = len(keymap[0])
    for r, row in enumerate(keymap):
        if len(row) != row_length:
            raise ValueError(f'All rows must have the same length (row {r})')
        for c, key in enumerate(row):
            keymap[r][c] = libevdev.evbit(key)
            device.enable(keymap[r][c])
            fn_keymap[r][c] = libevdev.evbit(fn_keymap[r][c])
            device.enable(fn_keymap[r][c])

    uinput = device.create_uinput_device()
    print(f'Created device {uinput.devnode}')
    return uinput, keymap, fn_keymap

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
        uinput, keymap, fn_keymap = create_device()
    # search keymap for fn key
    fn_key = None
    print("searching for fn key")
    for r, row in enumerate(config['keymap']):
        for c, key in enumerate(row):
            if key == "KEY_FN":
                print(f'Found fn key at {r}, {c}')
                fn_key = (r, c)
                break
        print("fn key not in row " + str(r))
    old_state = [[False for _ in config['keyboard_col_pins']] for _ in config['keyboard_row_pins']]
    repeat_states = [[{"down_time": 0, "last_repeat": 0} for _ in config['keyboard_col_pins']] for _ in config['keyboard_row_pins']]
    last_start = time.time()
    while True:
        for c, col_pin in enumerate(config['keyboard_col_pins']):
            key_states = test_col(col_pin, config['keyboard_row_pins'])
            for r, state in enumerate(key_states):
                if state == old_state[r][c]:
                    if state and time.time() - repeat_states[r][c]["down_time"] > config["repeat_start_delay_ms"]/1000 and time.time() - repeat_states[r][c]["last_repeat"] > config["repeat_interval_ms"]/1000:
                        print(f'Repeating {r}, {c} (key {config["keymap"][r][c]})')
                        if DO_SEND_KEYS:
                            if old_state[fn_key[0]][fn_key[1]]:
                                downevents = [libevdev.InputEvent(fn_keymap[r][c], 1), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                                upevents = [libevdev.InputEvent(fn_keymap[r][c], 0), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                            else:
                                downevents = [libevdev.InputEvent(keymap[r][c], 1), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                                upevents = [libevdev.InputEvent(keymap[r][c], 0), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                            uinput.send_events(downevents)
                            uinput.send_events(upevents)
                        repeat_states[r][c]["last_repeat"] = time.time()
                elif state:
                    print(f'Pressed {r}, {c} (key {config["keymap"][r][c]})')
                    repeat_states[r][c]["down_time"] = time.time()
                    if DO_SEND_KEYS:
                        if old_state[fn_key[0]][fn_key[1]]:
                            events = [libevdev.InputEvent(fn_keymap[r][c], 1), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                        else:
                            events = [libevdev.InputEvent(keymap[r][c], 1), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                        uinput.send_events(events)
                else:
                    print(f'Released {r}, {c} (key {config["keymap"][r][c]})')
                    if DO_SEND_KEYS:
                        if old_state[fn_key[0]][fn_key[1]]:
                            events = [libevdev.InputEvent(fn_keymap[r][c], 0), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                        else:
                            events = [libevdev.InputEvent(keymap[r][c], 0), libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]
                        uinput.send_events(events)
                old_state[r][c] = state
        time_elapsed = time.time() - last_start
        time.sleep(max(1/config['scanning_frequency']-time_elapsed,0))
        last_start = time.time()
    
if __name__ == '__main__':
    main()
