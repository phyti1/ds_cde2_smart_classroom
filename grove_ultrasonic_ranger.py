# based no https://github.com/Seeed-Studio/grove.py/blob/master/grove/grove_ultrasonic_ranger.py

#!/usr/bin/env python
#
# This is the code for Grove - Ultrasonic Ranger
# (https://www.seeedstudio.com/Grove-Ultrasonic-Ranger-p-960.html)
# which is a non-contact distance measurement module which works with 40KHz sound wave. 
#
# This is the library for Grove Base Hat which used to connect grove sensors for raspberry pi.
#

'''
## License
The MIT License (MIT)
Grove Base Hat for the Raspberry Pi, used to connect grove sensors.
Copyright (C) 2018  Seeed Technology Co.,Ltd. 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import time
import digitalio

usleep = lambda x: time.sleep(x / 1000000.0)

_TIMEOUT1 = 1000
_TIMEOUT2 = 10000
cycle_timeout = 10

class GroveUltrasonicRanger(object):
  def __init__(self, pin):
    self.dio = digitalio.DigitalInOut(pin)
    self.pin = pin

  def _get_distance(self):
    self.dio.direction = digitalio.Direction.OUTPUT
    self.dio.value = False
    usleep(2)
    self.dio.value = True
    usleep(10)
    self.dio.value = False

    self.dio.direction = digitalio.Direction.INPUT
    self.dio.pull = digitalio.Pull.DOWN

    t0 = time.monotonic_ns()
    count = 0
    while count < _TIMEOUT1:
      if self.dio.value:
        break
      count += 1
    # print(count)
    if count >= _TIMEOUT1:
      return None

    t1 = time.monotonic_ns()
    count = 0
    while count < _TIMEOUT2:
      if not self.dio.value:
        break
      count += 1
    if count >= _TIMEOUT2:
      return None


    t2 = time.monotonic_ns()
    #print((t2 - t1) / 1000000) # time in ms
    dt = int((t1 - t0) / 1000) # *  1000000
    if dt > 530:
      return None

    distance = (float(t2 - t1) / 1000 / 29 / 2)    # cm * 1000000
    return distance


  def get_distance(self):
    cycle = 0
    while cycle < cycle_timeout:
      dist = self._get_distance()
      #print(dist)
      if dist:
        return dist
      cycle += 1
    print("ERROR: Ultrasonic timeout reached")
    return None



# Grove = GroveUltrasonicRanger

# def main():
#     from grove.helper import SlotHelper
#     sh = SlotHelper(SlotHelper.GPIO)
#     pin = sh.argv2pin()

#     sonar = GroveUltrasonicRanger(pin)

#     print('Detecting distance...')
#     while True:
#         print('{} cm'.format(sonar.get_distance()))
#         time.sleep(1)

# if __name__ == '__main__':
#     main()