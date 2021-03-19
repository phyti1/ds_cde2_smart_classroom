import board
import time
import adafruit_scd30
import adafruit_requests as requests
import busio
from grove_ultrasonic_ranger import GroveUltrasonicRanger
import display
import pir
from grove_rgb_led import ChainableLED

from secrets import secrets

# connect to wifi
import wifi

# CO2
print("Connecting CO2")
i2c = busio.I2C(board.SCL, board.SDA)
scd = adafruit_scd30.SCD30(i2c)
print("Done")

# sonar
print("Connecting Ultrasonic")
sonar = GroveUltrasonicRanger(board.D9) # board D4
print("Done")

# LED
RGB_LED = ChainableLED(board.RX, board.TX, 1)

# main loop
while True:
    if scd.data_available:
        sonar_distance = sonar.get_distance()
        #display.show(round(sonar_distance))
        #time.sleep(1)
        display.show(round(scd.CO2))
        co2_color = int((scd.CO2 % 1000) / 1000 * 255)
        #print(co2_color)
        if scd.CO2 > 2000:
            RGB_LED.setColorRGB(1, 255, 0, 0)
        elif scd.CO2 > 1000:
            RGB_LED.setColorRGB(1, co2_color, co2_color, 0)
        else:
            RGB_LED.setColorRGB(1, 0, 255 - co2_color, 0)

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
