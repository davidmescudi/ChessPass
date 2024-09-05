from machine import ADC, Pin

class Potentiometer:
    def __init__(self, pin_num):
        # Initialize the potentiometer (ADC pin)
        self.adc = ADC(Pin(pin_num))
        self.adc.atten(ADC.ATTN_11DB)  # Set attenuation for full range of input voltage (0-3.3V)

    def read_value(self):
        # Read the potentiometer value and return it (0-4095 range for ESP32)
        return self.adc.read()
