import board
import digitalio
import time

class Pir:
    def __init__(self, pin):
        self.sensor = digitalio.DigitalInOut(pin) # nRF52840, Grove D4 board.A2
        self.sensor.direction = digitalio.Direction.INPUT
        self.sensor.pull = digitalio.Pull.UP

    def measure(self):
        return self.sensor.value