# use 'python3 comlog.py' to start or
# 'nohup python3 comlog.py &' with output in ./nohub.out

# use 'pkill -f comlog.py' to stop

import serial

# ls /dev/ttyAC*
port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=3.0)
print('serial opened')



while True:
    try:
        #port.write("\r\nSay something:")
        #rcv = port.read(10)
        response = port.readline().decode('utf-8')
        # print(response)
        # open or create file
        file = open("smartlog.log","a+")
        file.write(response)
        # close file
        file.close()
    except Exception as e:
        print(e)
