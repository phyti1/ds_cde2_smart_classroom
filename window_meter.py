import board
import time
import adafruit_scd30
import adafruit_requests as requests
import busio
import tm1637lib
import pulseio

from scheduler import Scheduler
from wifi import Wifi
from grove_ultrasonic_ranger import GroveUltrasonicRanger
from display import Display
from pir import Pir
from chainable_led import ChainableLED
from potentiometer import Potentiometer
from ntp_time import NtpTime
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

class WindowMeter:

    def __init__(self, is_debugging):
        self.is_debugging = is_debugging
        self.brightness = -1

    def __init_backend(self):
        # wifi
        print("Connecting Wifi")
        wifi = Wifi(secrets["ssid"], secrets["password"])
        wifi.connect()
        print("Connecting Wifi: Done")

        # buzzer
        print("Connecting Buzzer")
        cycle = 65535 // 5 # 20% power
        self.buzzer = pulseio.PWMOut(board.A0, duty_cycle=cycle, variable_frequency=True)
        # 100000 is not hearable
        self.buzzer.frequency = 100000
        print("Connecting Buzzer: Done")

        # CO2
        print("Connecting CO2")
        i2c = busio.I2C(board.SCL, board.SDA)
        self.scd = adafruit_scd30.SCD30(i2c)
        print("Connecting CO2: Done")

        # sonar
        print("Connecting Ultrasonic")
        self.sonar = GroveUltrasonicRanger(board.D9) # board D4
        print("Connecting Ultrasonic: Done")

        # LED
        print("Connecting LED")
        self.led = ChainableLED(board.RX, board.TX, 1)
        print("Connecting LED: Done")

        # Potentiometer
        print("Connecting Potentiometer")
        self.potentiometer = Potentiometer(board.A2)
        print("Connecting Potentiometer: Done")

        # Display
        print("Connecting Display")
        self.display = Display(board.A4, board.A5)
        print("Connecting Display: Done")

        # Pir
        print("Connecting Pir")
        self.pir = Pir(board.D5)
        print("Connecting Pir: Done")

        # real time
        print("Getting network time")
        self.ntp_time = NtpTime(wifi.get_esp())
        self.__load_network_time()
        print("Getting network time: Done")


    def __load_network_time(self):
        self.ntp_time.time()
    
    def __run_backend(self):
        self.__init_backend()
        
        print("Entering Main-Loop")
        # main loop
        while True:
            while not self.scd.data_available:
                print("SCD Data not avaliable.")
                time.sleep(0.5)
            
            sonar_distance = self.sonar.get_distance()
            #co2_color = int((scd.CO2 % 1000) / 1000 * 255)
            #print(co2_color)

            if round(self.scd.CO2) > 6000:
                self.buzzer.frequency = 880
                self.sched.sleep_ms(300)
                self.buzzer.frequency = 784
                self.sched.sleep_ms(700)
                self.buzzer.frequency = 100000

            is_pir_active = self.pir.measure()
            #display.show(str(is_pir_active))
            try:
                if not self.is_debugging:
                    print(requests.post(
                        secrets['endpoint'] + '/measurements',
                        json={
                            'sensor_uuid': secrets['uuid'],
                            'distance': sonar_distance,
                            'co2': self.scd.CO2,
                            'temperature': self.scd.temperature,
                            'humidity': self.scd.relative_humidity,
                            'movement': is_pir_active
                        },
                        headers={
                            'Authorization': 'Basic ' + secrets['oracle_token']
                        }
                    ).text)
                print("CO2:   " + str(self.scd.CO2))
                print("TEMPE: " + str(self.scd.temperature))
                print("HUMID: " + str(self.scd.relative_humidity))
                print("SONIC: " + str(sonar_distance))
                print("PIR:   " + str(is_pir_active))
                print("BRIGH: " + str(round(self.brightness, 2)))
                print()
            except Exception as e:
                print(e)
                pass
            # loop delay
            if self.is_debugging:
                self.sched.sleep_ms(2000)
            else:
                self.sched.sleep_ms(15000)

    def __check_frontend(self):
        self.display.show(round(self.scd.CO2))
        self.brightness = self.potentiometer.read_value_0to1()
        self.display.set_brightness(round(self.brightness * 7))
        self.led.set_brightness(self.brightness)
        if self.scd.CO2 > 2000:
            self.led.set_color_rgb(1, 255, 0, 0)
        elif self.scd.CO2 > 1000:
            self.led.set_color_rgb(1, 255, 255, 0)
        else:
            self.led.set_color_rgb(1, 0, 255, 0)

    def run(self):
        self.sched = Scheduler()
        self.sched.schedule_passive(self.__check_frontend, (), True)
        self.__run_backend()


        # print("frontend done")