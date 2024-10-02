from machine import ADC, Pin
from time import ticks_ms, ticks_diff

class HallSensor:
    def __init__(
        self,
        pin_num=36,
        hall_variance_threshold = 70,
        verbose = False,
        figure_detection_time = 1000,
        figure_detection_threshold = 0.3
    ):
        self.hall = ADC(Pin(pin_num))
        self.hall.atten(
            ADC.ATTN_11DB
        )  # Set the attenuation for the ADC pin to read the full 0-3.3V range
        self.hall_variance_threshold = hall_variance_threshold
        self.figure_detection_time = figure_detection_time
        self.figure_detection_threshold = figure_detection_threshold
        self.verbose = verbose
        self.baseline = 0 # sample before use!!
        self.initialised_time = None
        self.detected_history_avg = 0
    
    def log(self, *values):
        if self.verbose: print(*values)

    def read_value(self):
        return self.hall.read()  # Reads the analog value from the sensor

    def init_hall_sensor(self, samples=1000):
        
        readings = []

        for _ in range(samples):
            readings.append(self.hall.read())

        self.initialised_time = ticks_ms()
        # Calculate the average baseline
        self.baseline = sum(readings) // len(readings)
        self.log(f"Sensor initialized with baseline: {self.baseline}")
    
    def is_magnet_active_detected(self):
        #true_detected = sum(self.detected_history)

        return self.detected_history_avg#(true_detected / len(self.detected_history)) #>= self.figure_detection_threshold
        

    def is_magnet_detected(self):
        current_reading = self.hall.read()
        deviation = abs(current_reading - self.baseline)

        # Return True if deviation exceeds the threshold (magnet detected)
        isDetected = deviation > self.hall_variance_threshold
        #current_time = ticks_ms()

        if self.initialised_time:
            self.detected_history_avg = (self.detected_history_avg + int(isDetected)) / 2
            #if ticks_diff(current_time, self.initialised_time) >= self.figure_detection_time:
                # self.detected_history.append(isDetected)
                # self.detected_history.pop(0)
            # else:
            #     self.detected_history.append(isDetected)

        # Return True if deviation exceeds the threshold (magnet detected)
        return isDetected
    
