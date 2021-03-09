import board
import time
import adafruit_scd30
import adafruit_requests as requests
import busio
from grove_ultrasonic_ranger import GroveUltrasonicRanger
import display
import pir
import tm1637lib
import pulseio

from secrets import secrets

# connect to wifi
import wifi

# buzzer
cycle = 65535 // 5 # 20% power
buzzer = pulseio.PWMOut(board.A0,
  duty_cycle=cycle, variable_frequency=True)

# 100000 is not hearable
buzzer.frequency = 100000

# CO2
i2c = busio.I2C(board.SCL, board.SDA)
scd = adafruit_scd30.SCD30(i2c)

# sonar
sonar = GroveUltrasonicRanger(board.D9) # board D4


# main loop
while True:
    if scd.data_available:
        sonar_distance = sonar.get_distance()
        #display.show(round(sonar_distance))
        #time.sleep(1)
        display.show(round(scd.CO2))


        if round(scd.CO2) > 6000:
            buzzer.frequency = 880
            time.sleep(0.3)
            buzzer.frequency = 784
            time.sleep(0.7)
            buzzer.frequency = 100000


        is_pir_active = pir.measure()
        #display.show(str(is_pir_active))
        try:
            print(requests.post(secrets['endpoint'], json={
                'device': secrets['device'],
                'sonar': sonar_distance,
                'co2': scd.CO2,
                'temperature': scd.temperature,
                'humidity': scd.relative_humidity,
                'is_pir_active': is_pir_active
            }).text)
            print("CO2:   " + str(scd.CO2))
            print("TEMP:  " + str(scd.temperature))
            print("HUMI:  " + str(scd.relative_humidity))
            print("SONIC: " + str(sonar_distance))
            print("PIR:   " + str(is_pir_active))
            print()
        except Exception as e:
            print(e)
            pass
    #time.sleep(10)
