import time
import board
import busio
from adafruit_ntp import NTP

class NtpTime:
    def __init__(self, esp):
        self.esp = esp
        # The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
        self.host = "pool.ntp.org"

    #https://github.com/adafruit/Adafruit_CircuitPython_NTP/blob/master/examples/ntp_simpletest.py
    def time(self):
        # spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        # esp = adafruit_esp32spi.ESP_SPIcontrol(spi, self.wifi. esp32_cs, esp32_ready, esp32_reset)

        # print("Connecting to AP...")
        # while not esp.is_connected:
        #     try:
        #         esp.connect_AP(b"WIFI_SSID", b"WIFI_PASS")
        #     except RuntimeError as e:
        #         print("could not connect to AP, retrying: ", e)
        #         continue

        # Initialize the NTP object
        ntp = NTP(self.esp)

        # Fetch and set the microcontroller's current UTC time
        # keep retrying until a valid time is returned
        while not ntp.valid_time:
            ntp.set_time()
            print("Failed to obtain time, retrying in 5 seconds...")
            time.sleep(5)

        # Get the current time in seconds since Jan 1, 1970
        current_time = time.time()
        print("Seconds since Jan 1, 1970: {} seconds".format(current_time))

        # Convert the current time in seconds since Jan 1, 1970 to a struct_time
        now = time.localtime(current_time)
        #print(now)

        # Pretty-parse the struct_time
        print("It is currently {}.{}.{} {}:{}:{} UTC".format( now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))

