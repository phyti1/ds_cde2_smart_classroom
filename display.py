import board
import tm1637lib

class Display:
    def __init__(self, clk, dio):
        self.display = tm1637lib.Grove4DigitDisplay(clk, dio) #board.A4, board.A5
        self.co2 = ''
        self.error = ''
        self.position = 0
        self.brightness = 0
        self.co2delay = 0
        self.offthreshold = 0.05

    def set_brightness(self, brightness):
        # print(brightness)
        self.brightness = brightness
        if self.brightness < self.offthreshold:
            self.display.clear()
        else:
            # tune brightness because of rounding happened earlier and to be able to see it when led is off
            self.brightness = round(brightness * 7)
            self.display.set_brightness(self.brightness)

    def set_co2(self, value):
        self.co2 = value
        self.show()
    
    def set_error(self, value):
        self.error = value
        self.show()

    def show(self):
        if self.brightness >= self.offthreshold:
            raw_data = f'{str(self.co2)} {self.error}    '

            # slice data
            data = raw_data[self.position:self.position + 4]
            if self.position >= len(raw_data):
                self.position = 0
                self.co2delay = 0
            else:
                # only move window if error exist
                if len(self.error) > 0:
                    if self.co2delay < 3:
                        self.co2delay += 1
                    else:
                        # move window
                        self.position += 1
            
            # show upper case because more letters exist there
            self.display.show(data)
