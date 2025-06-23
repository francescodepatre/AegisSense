import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import datetime

class PanTiltController:
    def __init__(self, pan_channel, tilt_channel, pan_limits=(0,180), tilt_limits=(0,180), logf=None, commInterface=None):
        self.pan_channel = pan_channel
        self.tilt_channel = tilt_channel
        self.pan_limits = pan_limits
        self.tilt_limits = tilt_limits
        self.logfile = logf
        self.i2c = commInterface or busio.I2C(SCL, SDA)

        self.default_pan_angle = 90
        self.default_tilt_angle = 90

        self.setup_hardware()

    def writeOnLog(self,e):
        with open(self.logfile, "a") as logFile:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logFile.write(f"{timestamp} - {e}\n")

    def setup_hardware(self):
        try:
            self.pca = PCA9685(self.i2c)
            self.pca.frequency = 50
            print("[INFO] PCA9685 initialized.")
        except Exception as e:
            print("[ERROR] PCA9685 setup failed:", e)

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
            event = f"HARDWARE SUPPORT [PAN] --- moving pan to: {angle}"
            self.writeOnLog(event)
            self.pca.channels[self.pan_channel].duty_cycle = pwm
        except Exception as e:
            event = f"ERROR PAN MOVEMENT - {str(e)}\n"
            self.writeOnLog(event)


    def move_tilt(self,angle):
        angle = max(self.tilt_limits[0], min(self.tilt_limits[1],angle))
        self.tilt_angle = angle
        pwm = self.angle_to_pwm(angle)
        try:
            event = f"HARDWARE SUPPORT [TILT] --- moving tilt to: {angle}"
            self.writeOnLog(event)
            self.pca.channels[self.tilt_channel].duty_cycle = pwm
        except Exception as e:
            event = f"ERROR TILT MOVEMENT - {str(e)}\n"
            self.writeOnLog(event)

    def get_pan(self):
        return self.pan_angle
    
    def get_tilt(self):
        return self.tilt_angle
    
    def sweep_pan(self, start_pan, end_pan, step=5, delay=0.1):
        for angle in range(start_pan,end_pan + 1, step):
            self.move_pan(angle)
            time.sleep(delay)
        
        for angle in range(end_pan, start_pan + 1, -step):
            self.move_pan(angle)
            time.sleep(delay)
        
    def sweep_tilt(self, start_tilt, end_tilt, step=5, delay=0.1):
        for angle in range(start_tilt,end_tilt + 1, step):
            self.move_tilt(angle)
            time.sleep(delay)
        
        for angle in range(end_tilt, start_tilt + 1, -step):
            self.move_tilt(angle)
            time.sleep(delay)

    def center(self):
        self.move_pan(90)
        time.sleep(1)
        self.move_tilt(90)
        time.sleep(1)

    def shutdown(self):
        event = "Shutting down: disabling PWM outputs."
        self.writeOnLog(event)
        self.center()
        time.sleep(1)
        self.move_tilt(160)
        time.sleep(1)
        try:
            self.pca.channels[self.pan_channel].duty_cycle = 0
            self.pca.channels[self.tilt_channel].duty_cycle = 0
        except Exception as e:
            event = f"ERROR SHUTDOWN - {str(e)}\n"
            self.writeOnLog(event)

    def research_loop(self):
        self.sweep_pan(0,180)

    

    def test_hardware_support(self):
        try:
            self.center()
            time.sleep(1)
            self.sweep_pan(0,180)
            time.sleep(1)
            self.center()
            time.sleep(1)
            self.sweep_tilt(0,120)
            time.sleep(1)
            self.center()
            time.sleep(1)
            return True
        except:
            return False

        
