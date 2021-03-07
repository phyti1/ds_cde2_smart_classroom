import board
import digitalio
import time
from grove_ultrasonic_ranger import GroveUltrasonicRanger

# setup 
sonar = GroveUltrasonicRanger(board.D9) # board D4

# main loop
print('Detecting distance...')
while True:
    dist = sonar.get_distance()
    print('{} cm'.format(dist))
    time.sleep(1)



