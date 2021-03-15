import board
import digitalio
import time

sensor = digitalio.DigitalInOut(board.A2) # nRF52840, Grove D4
sensor.direction = digitalio.Direction.INPUT
sensor.pull = digitalio.Pull.UP

def measure():
    return sensor.value