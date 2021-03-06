import board
import digitalio
import time
import pulseio

# setup 
cycle = 65535 // 5 # 20% power
buzzer = pulseio.PWMOut(board.A0, duty_cycle=cycle, variable_frequency=True)

# main loop
while True:
    print("off")
    # time.sleep(0.1)
    for f in (262, 294, 330, 392):
        buzzer.frequency = f
        time.sleep(0.1)