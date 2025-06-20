import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import datetime

class PanTiltController:
    def __init__(self, pan_channel, tilt_channel, pan_limits=(0,180), tilt_limits=(0,180), logf=None, commInteface=None):
        self.pan_channel = pan_channel
        self.tilt_channel = tilt_channel
        self.pan_limits = pan_limits
        self.tilt_limits = tilt_limits
        self.logfile = logf
        self.i2c = commInteface or busio.I2C(SCL, SDA)

        self.default_pan_angle = 90
        self.default_tilt_angle = 90

        self.setup_hardware()

    def setup_hardware(self):
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50

    def angle_to_pwm(self, angle):
        min_pulse = 1000
        max_pulse = 2000
        pulse = int(min_pulse + (angle / 180) * (max_pulse - min_pulse))
        duty = int(pulse * 65535 / (1000000 / self.pca.frequency))
        return duty

    def move_pan(self,angle):
        angle = max(self.pan_limits[0], min(self.pan_limits[1], angle))
        self.pan_angle = angle
        pwm = self.angle_to_pwm(angle)
        try:
            print("HARDWARE SUPPORT [PAN] --- moving pan to: ", angle)
            self.pca.channels[self.pan_channel].duty_cycle = pwm
        except Exception as e:
            print("ERROR! Cannot move pan!")
            if self.logfile:
                with open(self.logfile, "a") as logFile:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logFile.write(f"{timestamp} ERROR PAN MOVEMENT - {str(e)}\n")


    def move_tilt(self,angle):
        angle = max(self.tilt_limits[0], min(self.tilt_limits[1],angle))
        self.tilt_angle = angle
        pwm = self.angle_to_pwm(angle)
        try:
            print("HARDWARE SUPPORT [TILT] --- moving tilt to: ", angle)
            self.pca.channels[self.tilt_channel].duty_cycle = pwm
        except Exception as e:
            print("ERROR! Cannot move tilt!")
            if self.logfile:
                with open(self.logfile, "a") as logFile:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logFile.write(f"{timestamp} - ERROR TILT MOVEMENT - {str(e)}\n")

    def get_pan(self):
        return self.pan_angle
    
    def get_tilt(self):
        return self.tilt_angle
    
    def sweep(self, start_pan, end_pan, step=5, delay=0.1):
        for angle in range(start_pan,end_pan + 1, step):
            self.move_pan(angle)
            time.sleep(delay)

    def center(self):
        self.move_pan(90)
        self.move_tilt(90)
