from machine import ADC, Pin

class HallSensor:
    def __init__(
        self,
        pin_num=36,
        hall_variance_threshold = 70,
        morse_variance = 5,
        verbose = False
    ):
        self.hall = ADC(Pin(pin_num))
        self.hall.atten(
            ADC.ATTN_11DB
        )  # Set the attenuation for the ADC pin to read the full 0-3.3V range
        self.hall_variance_threshold = hall_variance_threshold
        self.morse_variance = morse_variance
        self.verbose = False
        self.baseline = self.init_hall_sensor() # average sample
    
    def log(self, *values):
        if self.verbose: print(*values)

    def read_value(self):
        return self.hall.read()  # Reads the analog value from the sensor

    def init_hall_sensor(self, samples=1000):
        
        readings = []

        for _ in range(samples):
            readings.append(self.hall.read())

        # Calculate the average baseline
        self.baseline = sum(readings) // len(readings)
        self.log(f"Sensor initialized with baseline: {self.baseline}")
        
    def is_magnet_detected(self):
        current_reading = self.hall.read()
        deviation = abs(current_reading - self.baseline)

        # Return True if deviation exceeds the threshold (magnet detected)
        return deviation > self.hall_variance_threshold
    
