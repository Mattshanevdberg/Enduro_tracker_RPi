import serial
ser=serial.Serial(port='/dev/serial0', baudrate=9600, timeout=1, parity= serial.PARITY_NONE)
ser.flushInput()
ser.flushOutput()
ser.write(bytearray([0xD1])) # get information instruction
test = ser.read(9)
print(test)
