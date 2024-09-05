from machine import Pin, PWM

class Electromagnet:
    def __init__(self, pin_num, frequency=1000):
        # Initialize the pin as PWM for controlling the electromagnet with duty cycle 0
        self.pin = Pin(pin_num, Pin.OUT)
        self.pwm = PWM(self.pin, freq=frequency)
        self.pwm.duty(0)

    def set_power(self, duty_cycle):
        # Set the power level of the electromagnet using PWM duty cycle (0-1023 for ESP32)
        duty_cycle = max(0, min(1023, duty_cycle))  # Clamp the value between 0 and 1023
        self.pwm.duty(duty_cycle)
        print(f"Electromagnet power set to {duty_cycle}/1023")
