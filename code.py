import neopixel
import board
from window_meter import WindowMeter

# disable status led
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
led.brightness = 0.0

# Program entry-point
main = WindowMeter(is_debugging=True)
main.run()