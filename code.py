import board
import time
import adafruit_scd30
import adafruit_requests as requests
import busio
import tm1637lib
import pulseio

from wifi import Wifi
from grove_ultrasonic_ranger import GroveUltrasonicRanger
from display import Display
from pir import Pir
from chainable_led import ChainableLED
from potentiometer import Potentiometer
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

is_debugging = True

# wifi
print("Connecting Wifi")
Wifi(secrets["ssid"], secrets["password"]).connect()
print("Connecting Wifi: Done")

# buzzer
print("Connecting CO2")
cycle = 65535 // 5 # 20% power
buzzer = pulseio.PWMOut(board.A0, duty_cycle=cycle, variable_frequency=True)
# 100000 is not hearable
buzzer.frequency = 100000
print("Connecting CO2: Done")

# CO2
print("Connecting CO2")
i2c = busio.I2C(board.SCL, board.SDA)
scd = adafruit_scd30.SCD30(i2c)
print("Connecting CO2: Done")

# sonar
print("Connecting Ultrasonic")
sonar = GroveUltrasonicRanger(board.D9) # board D4
print("Connecting Ultrasonic: Done")

# LED
print("Connecting LED")
led = ChainableLED(board.RX, board.TX, 1)
print("Connecting LED: Done")

# Potentiometer
print("Connecting Potentiometer")
potentiometer = Potentiometer(board.A2)
print("Connecting Potentiometer: Done")

# Display
print("Connecting Display")
display = Display(board.A4, board.A5)
print("Connecting Display: Done")

# Pir
print("Connecting Pir")
pir = Pir(board.D5)
print("Connecting Pir: Done")

print("Entering Main-Loop")
# main loop
while True:
    if not scd.data_available:
        print("SCD Data not avaliable.")
    else:
        sonar_distance = sonar.get_distance()
        display.show(round(scd.CO2))
        brightness = potentiometer.read_value_0to1()
        display.set_brightness(round(brightness * 7))
        led.set_brightness(brightness)
        #co2_color = int((scd.CO2 % 1000) / 1000 * 255)
        #print(co2_color)
        if scd.CO2 > 2000:
            led.set_color_rgb(1, 255, 0, 0)
        elif scd.CO2 > 1000:
            led.set_color_rgb(1, 255, 255, 0)
        else:
            led.set_color_rgb(1, 0, 255, 0)

        if round(scd.CO2) > 6000:
            buzzer.frequency = 880
            time.sleep(0.3)
            buzzer.frequency = 784
            time.sleep(0.7)
            buzzer.frequency = 100000

        is_pir_active = pir.measure()
        #display.show(str(is_pir_active))
        try:
            if not is_debugging:
                print(requests.post(
                    secrets['endpoint'] + '/measurements',
                    json={
                        'sensor_uuid': secrets['uuid'],
                        'distance': sonar_distance,
                        'co2': scd.CO2,
                        'temperature': scd.temperature,
                        'humidity': scd.relative_humidity,
                        'movement': is_pir_active
                    },
                    headers={
                        'Authorization': 'Basic ' + secrets['oracle_token']
                    }
                ).text)
            print("CO2:   " + str(scd.CO2))
            print("TEMPE: " + str(scd.temperature))
            print("HUMID: " + str(scd.relative_humidity))
            print("SONIC: " + str(sonar_distance))
            print("PIR:   " + str(is_pir_active))
            print("BRIGH: " + str(round(brightness, 2)))
            print()
        except Exception as e:
            print(e)
            pass
    # loop delay
    if is_debugging:
        time.sleep(2)
    else:
        time.sleep(15)
