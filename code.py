import neopixel
import board
from window_meter import WindowMeter
import time
import gc

# disable status led
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
led.brightness = 0.0

# memory overflow test
# while True:
#     try:
#         i = 2
#         while True:
#             i = i ** 2
#             time.sleep(0.1)
#             print(gc.mem_free())
#     except Exception as e:
#         print(e)

# Program entry-point
main = WindowMeter(is_debugging=False)
main.run()
