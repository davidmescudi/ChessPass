from machine import ADC, Pin

class HallSensor:
    def __init__(self, pin_num):
        self.adc = ADC(Pin(pin_num))
        self.adc.atten(ADC.ATTN_11DB)  # Set the attenuation for the ADC pin to read the full 0-3.3V range

    def read_value(self):
        return self.adc.read()  # Reads the analog value from the sensor
