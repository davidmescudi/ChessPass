from machine import Pin, ADC, PWM
from time import sleep

led = Pin(9, Pin.OUT)
led.on()
pwm_pin = Pin(8)
pwm = PWM(pwm_pin, freq=1000)  # Set frequency to 1kHz

clk = Pin(7, Pin.IN, Pin.PULL_UP)
dt = Pin(44, Pin.IN, Pin.PULL_UP)

# Define the pin for PWM output (e.g., GPIO 32)


# Initial duty cycle
duty = 800  # (0 to 1023)
pwm.duty(duty)

# Variables to track encoder state
last_clk = clk.value()

def read_encoder():
    global last_clk, duty

    current_clk = clk.value()


    if current_clk == 1 and last_clk == 0:
        led.off()
        if dt.value() == 0:  # Clockwise rotation
            duty += 50
        else:  # Counter-clockwise rotation
            duty -= 50
            
        # Limit duty cycle between 0 and 1023
        duty = max(0, min(duty, 1023))
        pwm.duty(duty)
        print("Duty cycle:", duty)

    # Update last state
    last_clk = current_clk


def avg(xs):
    return sum(xs) // len(xs)

while True:
    read_encoder()
    
    sleep(0.01)



