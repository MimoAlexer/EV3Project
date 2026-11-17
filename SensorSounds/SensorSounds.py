#!/usr/bin/env python3
import signal
import subprocess
from pathlib import Path
from time import monotonic, sleep

from ev3dev.ev3 import Button, ColorSensor, Leds, TouchSensor


def terminate(*_):
    raise SystemExit


def main():
    buttons = Button()
    touch = TouchSensor('in1')
    sensor = ColorSensor('in3')
    leds = Leds()
    audio = None
    directory = Path(__file__).resolve().parent
    mode = 'COL-COLOR'
    previous_buttons = set(buttons.buttons_pressed)
    previous_value = None
    candidate = None
    candidate_since = monotonic()

    def stop_audio():
        nonlocal audio
        if audio is not None:
            if audio.poll() is None:
                audio.terminate()
            audio.wait()
            audio = None

    def play(filename, color):
        nonlocal audio
        stop_audio()
        leds.set_color(leds.LEFT, color)
        leds.set_color(leds.RIGHT, color)
        audio = subprocess.Popen(['aplay', '-q', str(directory / filename)])

    signal.signal(signal.SIGTERM, terminate)
    try:
        sensor.mode = mode
        sleep(0.1)
        leds.set_color(leds.LEFT, leds.GREEN)
        leds.set_color(leds.RIGHT, leds.GREEN)
        print('Left/right: sounds | Up: color | Down: brightness')
        print('Touch sensor or Back: stop')
        while not touch.is_pressed:
            pressed = set(buttons.buttons_pressed)
            new_buttons = pressed - previous_buttons
            previous_buttons = pressed
            if 'backspace' in pressed:
                break
            if 'left' in new_buttons:
                play('pigeon.wav', leds.GREEN)
            elif 'right' in new_buttons:
                play('effect.wav', leds.RED)
            selected_mode = mode
            if 'up' in new_buttons:
                selected_mode = 'COL-COLOR'
            elif 'down' in new_buttons:
                selected_mode = 'COL-AMBIENT'
            if selected_mode != mode:
                mode = selected_mode
                sensor.mode = mode
                previous_value = None
                candidate = None
                print('Mode: ' + mode)
                sleep(0.1)
            value = sensor.value()
            if mode == 'COL-AMBIENT':
                # Hysteresis avoids repeated sounds near the threshold.
                threshold = 25 if previous_value == 1 else 35
                value = int(value >= threshold)
            if value != candidate:
                candidate = value
                candidate_since = monotonic()
            elif monotonic() - candidate_since >= 0.2 and value != previous_value:
                if previous_value is not None:
                    if mode == 'COL-COLOR':
                        play('pigeon.wav', leds.ORANGE)
                    else:
                        play('effect.wav', leds.GREEN if value else leds.RED)
                previous_value = value
            sleep(0.02)
    finally:
        stop_audio()
        leds.all_off()


if __name__ == '__main__':
    main()
