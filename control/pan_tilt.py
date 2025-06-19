import time

class PanTiltController:
    def __init__(self, pan_channel, tilt_channel, pan_limits=(0,180), tilt_limits=(0,180)):
        self.pan_channel = pan_channel
        self.tilt_channel = tilt_channel
        self.pan_limits = pan_limits
        self.tilt_limits = tilt_limits

        self.default_pan_angle = 90
        self.default_tilt_angle = 90

        self.setup_hardware()

    def setup_hardware():
        #inizializza i pin, PWM ecc
        return

    def move_pan(self,angle):
        angle = max(self.pan_limits[0], min(self.pan_limits[1], angle))
        self.pan_angle = angle

        #AGGIUNGERE COMANDO E CONTROLLI DI SICUREZZA

    def move_tilt(self,angle):
        angle = max(self.tilt_limits[0], min(self.tilt_limits[1],angle))
        self.tilt_angle = angle

        #AGGIUNGERE COMANDO E CONTROLLI DI SICUREZZA

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


if __name__ == "__main__":
    controller = PanTiltController(pan_channel=17, tilt_channel=18)

    controller.center()
    time.sleep(1)

    controller.sweep(60, 120, step=10, delay=0.5)

    controller.move_tilt(45)
    time.sleep(1)

    controller.center()