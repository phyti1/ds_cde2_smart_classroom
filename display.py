import board
import tm1637lib

class Display:
    def __init__(self, clk, dio):
        self.display = tm1637lib.Grove4DigitDisplay(clk, dio) #board.A4, board.A5

    def show(self, content):
        self.display.show(content)

    def set_brightness(self, brightness):
        self.display.set_brightness(brightness)