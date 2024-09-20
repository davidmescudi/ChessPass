from machine import Pin, PWM
from time import sleep, sleep_ms

# Define the pins for the rotary encoder
clk = Pin(4, Pin.IN, Pin.PULL_UP)
dt = Pin(5, Pin.IN, Pin.PULL_UP)

# Define the pin for PWM output (e.g., GPIO 32)
pwm_pin = Pin(6)
pwm = PWM(pwm_pin, freq=1000)  # Set frequency to 1kHz

# Initial duty cycle
duty = 512  # Midpoint (0 to 1023)
pwm.duty(duty)

# Variables to track encoder state
last_clk = clk.value()

def read_encoder():
    global last_clk, duty

    current_clk = clk.value()


    if current_clk == 1 and last_clk == 0:
        if dt.value() == 0:  # Clockwise rotation
            duty += 10
        else:  # Counter-clockwise rotation
            duty -= 10
            
        # Limit duty cycle between 0 and 1023
        duty = max(0, min(duty, 1023))
        pwm.duty(duty)
        print("Duty cycle:", duty)

    # Update last state
    last_clk = current_clk

# Main loop
while True:
    read_encoder()
    sleep_ms(2)  # Small delay for debouncing
