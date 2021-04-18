import serial

# ls /dev/serial*
port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=3.0)
print('serial opened')



while True:
    #port.write("\r\nSay something:")
    #rcv = port.read(10)
    response = port.readline()
    # open or create file
    file = open("smartlog.log","a+")
    file.write(response)
    # close file
    file.close()
    #print(response)
