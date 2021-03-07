import board
import time
import adafruit_scd30
import adafruit_requests as requests
import busio
from grove_ultrasonic_ranger import GroveUltrasonicRanger

from secrets import secrets

# connect to wifi
import wifi

# CO2
i2c = busio.I2C(board.SCL, board.SDA)
scd = adafruit_scd30.SCD30(i2c)

# sonar
sonar = GroveUltrasonicRanger(board.D9) # board D4


# main loop
while True:
    if scd.data_available:
        sonar_distance = sonar.get_distance()
        try:
            print(requests.post(secrets['endpoint'], json={
                'device': secrets['device'],
                'sonar': sonar_distance,
                'co2': scd.CO2,
                'temperature': scd.temperature,
                'humidity': scd.relative_humidity
            }).text)
        except:
            print('Server error!')
            pass
    time.sleep(10)
