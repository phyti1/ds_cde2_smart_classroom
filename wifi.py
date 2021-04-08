# SPDX-FileCopyrightText: 2019 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi


class Wifi:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password

    def initialize(self):

        print("ESP32 SPI webclient test")

        esp32_cs = DigitalInOut(board.D13)
        esp32_ready = DigitalInOut(board.D11)
        esp32_reset = DigitalInOut(board.D12)

        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        # class property to be able to access it from outside
        self.esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

        requests.set_socket(socket, self.esp)

    def connect(self):
        if self.esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
            print("ESP32 found and in idle mode")

        print("Connecting to AP...")
        while not self.esp.is_connected:
            try:
                self.esp.connect_AP(self.ssid, self.password) # secrets["ssid"], secrets["password"]
            except RuntimeError as e:
                print("could not connect to AP, retrying: ", e)
                continue
        print("Connected to", str(self.esp.ssid, "utf-8"), "\tRSSI:", self.esp.rssi)
        print("My IP address is", self.esp.pretty_ip(self.esp.ip_address))
        print("Ping google.com: %d ms" % self.esp.ping("google.com"))
        print("Done!")

    def get_esp(self):
        return self.esp