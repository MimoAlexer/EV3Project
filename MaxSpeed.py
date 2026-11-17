#!/usr/bin/env python3
import signal
from time import sleep

from ev3dev.ev3 import Button, LargeMotor


def terminate(*_):
    raise SystemExit


def main():
    motors = [LargeMotor(port) for port in ('outB', 'outC')]
    buttons = Button()
    signal.signal(signal.SIGTERM, terminate)
    try:
        for motor in motors:
            motor.run_direct(duty_cycle_sp=100)
        while buttons.enter:
            sleep(0.02)
        while not buttons.enter:
            sleep(0.02)
    finally:
        for motor in motors:
            motor.stop(stop_action='brake')


if __name__ == '__main__':
    main()
