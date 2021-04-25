import board
import time
import adafruit_scd30
import adafruit_requests as requests
import busio
import tm1637lib
import pulseio
import gc
import sys

from scheduler import Scheduler
from wifi import Wifi
from grove_ultrasonic_ranger import GroveUltrasonicRanger
from display import Display
from pir import PIR
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
        print("Connecting Wifi.")
        self.wifi = Wifi(secrets["ssid"], secrets["password"])
        self.wifi.initialize()
        self.wifi.connect()
        print("Connecting Wifi: Done.")

        # buzzer
        print("Connecting Buzzer.")
        cycle = 65535 // 5 # 20% power
        self.buzzer = pulseio.PWMOut(board.A0, duty_cycle=cycle, variable_frequency=True)
        # 100000 is not hearable
        self.buzzer.frequency = 100000
        print("Connecting Buzzer: Done.")

        # CO2
        print("Connecting CO2.")
        i2c = busio.I2C(board.SCL, board.SDA)
        self.scd = adafruit_scd30.SCD30(i2c)
        print("Connecting CO2: Done.")

        # sonar
        print("Connecting Ultrasonic.")
        self.sonar = GroveUltrasonicRanger(board.D9) # board D4
        print("Connecting Ultrasonic: Done.")

        # LED
        print("Connecting LED.")
        self.led = ChainableLED(board.RX, board.TX, 1)
        print("Connecting LED: Done.")

        # Potentiometer
        print("Connecting Potentiometer.")
        self.potentiometer = Potentiometer(board.A2)
        print("Connecting Potentiometer: Done.")

        # Display
        print("Connecting Display.")
        self.display = Display(board.A4, board.A5)
        print("Connecting Display: Done.")

        # Pir
        print("Connecting Pir.")
        self.pir = PIR(board.D5)
        print("Connecting Pir: Done.")

        # real time
        print("Getting network time.")
        self.ntp_time = NtpTime(self.wifi.get_esp())
        self.__load_network_time()
        print("Getting network time: Done.")


    def __load_network_time(self):
        self.ntp_time.time()

    def __handle_offline(self, is_offline, values):
        filename = 'offline.txt'
        # try open file
        try:
            local_file = open(filename, "rw")
            # continue with the file.
        except OSError:  # open failed
            local_file = open(filename, 'x')

            if is_offline:
                # offline, write values to file
                print(f"Adding line to {filename} file.")
                line = ''
                for value in values:
                    line += f'{value},'
                local_file.write(line + '\n')
                print("Done adding line.")
            else:
                # online, publish content
                print("Checking for offline values.")
                content = local_file.read()
                lines = content.split('\n')
                for line in lines:
                    values = line.split(',')
                    # upload offline values
                    print(f"Posting values <{values}> to the database.")
                    response = requests.post(
                        secrets['endpoint'] + '/measurements',
                        json={
                            'sensor_uuid': values[0],
                            'distance': values[1],
                            'co2': values[2],
                            'temperature': values[3],
                            'humidity': values[4],
                            'movement': values[5]
                        },
                        headers={
                            'Authorization': 'Basic ' + secrets['oracle_token']
                        }
                    )
                    print(response.text)
                    print(f"Posting values <{values}> to the database: Done.")
                    # remove from content because it is now handled
                    content = content.replace(line, '')
                # write changes to file
                local_file.write(content)
                print("Checking for offline values: Done.")
            
            local_file.close()
        except Exception as e:
            print(f"Failed handling offline: {e}")
            sys.print_exception(e)


    def __run_backend(self):
        self.__init_backend()
        # ensure restart incase of error
        while True:
            try:
                print("Entering Main-Loop")
                # main loop
                while True:
                    while not self.scd.data_available:
                        print("SCD Data not yet avaliable.")
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
                    if not self.is_debugging:
                        try:
                            def send_data(self):
                                response = requests.post(
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
                                )
                                # print(response.headers)
                                # print(response.content)
                                print(response.text)
                                # TODO make file system accessable!!
                                # self.__handle_offline(False, [])

                            try:
                                send_data(self)
                                self.display.set_error('')
                            except:
                                # if no internet retry after reconnecting the wifi module
                                self.wifi.reconnect()
                                send_data(self)
                                self.display.set_error('')
                        except Exception as e:
                            print('no internet, writing to file')
                            sys.print_exception(e)
                            self.display.set_error('OFFLInE')
                            # TODO make file system accessable!!
                            # self.__handle_offline(True, [secrets['uuid'], sonar_distance, self.scd.CO2, self.scd.temperature, self.scd.relative_humidity, is_pir_active])


                    print("CO2:   " + str(self.scd.CO2))
                    print("TEMPE: " + str(self.scd.temperature))
                    print("HUMID: " + str(self.scd.relative_humidity))
                    print("SONIC: " + str(sonar_distance))
                    print("PIR:   " + str(is_pir_active))
                    print("BRIGH: " + str(round(self.brightness, 2)))
                    print()
                    # loop delay
                    if self.is_debugging:
                        # test system values
                        print(time.monotonic_ns())
                        print(f'memory old: {gc.mem_free()}')
                        gc.collect()
                        print(f'memory new: {gc.mem_free()}')
                        self.sched.sleep_ms(2000)
                    else:
                        gc.collect()
                        self.sched.sleep_ms(15000)
            except Exception as e:
                print('Main Loop crashed with exception:')
                print(e)
                sys.print_exception(e)
                # if not self.is_debugging:
                #     print('Try logging to REST API...')
                #     try:
                #         response = requests.post(
                #             secrets['endpoint'] + '/logs',
                #             json={
                #                 'sensor_uuid': secrets['uuid'],
                #                 'log_msg': str(e),
                #                 'log_level': 'error',
                #             },
                #             headers={
                #                 'Authorization': 'Basic ' + secrets['oracle_token']
                #             }
                #         )
                #         print(response.text)
                #         print('Log sent.')
                #         self.wifi.connect()
                #     except Exception as e:
                #         print('no internet')
                #         print(e)

    def __check_frontend(self):
        self.display.set_co2(round(self.scd.CO2))
        self.brightness = self.potentiometer.read_value_0to1()
        self.display.set_brightness(self.brightness)
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