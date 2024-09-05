from lib.electromagnet import Electromagnet
from lib.potentiometer import Potentiometer
import time

# Constants
PWM_MAX_DUTY = 1023  # ESP32 PWM duty cycle max is 1023
ADC_MAX_VALUE = 4095  # ESP32 ADC max value is 4095

# Initialize the electromagnet on a specific pin
electromagnet = Electromagnet(pin_num=25)

# Initialize the potentiometer on a specific pin
potentiometer = Potentiometer(pin_num=32)

def map_value(value, in_min, in_max, out_min, out_max):
    # Map a value from one range to another
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def main():
    while True:
        # Read the potentiometer value
        pot_value = potentiometer.read_value()
        
        # Map the potentiometer value (0-4095) to a PWM duty cycle (0-1023)
        pwm_value = map_value(pot_value, 0, ADC_MAX_VALUE, 0, PWM_MAX_DUTY)
        
        # Set the PWM duty cycle for the electromagnet
        electromagnet.set_power(pwm_value)
        
        # Add a small delay to prevent overwhelming the CPU
        time.sleep(0.1)

if __name__ == "__main__":
    main()
