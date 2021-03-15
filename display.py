import board
import tm1637lib

display = tm1637lib.Grove4DigitDisplay(board.A4, board.A5)

def show(content):
    display.show(content)