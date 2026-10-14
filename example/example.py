import time
from MotoPi import MotoPi
from adafruit_motor import servo

# open MotoPi as motopi
with MotoPi(address=0x41, enable_pin=7) as motopi:
    # set frequency of MotoPi
    motopi.frequency = 50
    # declare servo channel 0 of MotoPi
    servo0 = servo.Servo(motopi.channels[0])
    # move servo from position 0 to 180
    for i in range(180):
        servo0.angle = i
        time.sleep(0.03)
    # move servo from position 0 to 180
    for i in range(180):
        servo0.angle = 180 - i
        time.sleep(0.03)