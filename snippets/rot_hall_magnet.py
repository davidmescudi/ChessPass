from machine import Pin, ADC, PWM
from time import sleep

hall = ADC(Pin(3)) 
hall.atten(ADC.ATTN_11DB)
#hall = Pin(3, Pin.IN)
#dig = Pin(6, Pin.IN)

clk = Pin(4, Pin.IN, Pin.PULL_UP)
dt = Pin(5, Pin.IN, Pin.PULL_UP)

# Define the pin for PWM output (e.g., GPIO 32)
pwm_pin = Pin(2)
pwm = PWM(pwm_pin, freq=1000)  # Set frequency to 1kHz

# Initial duty cycle
duty = 800  # Midpoint (0 to 1023)
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


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def avg(xs):
    return sum(xs) // len(xs)

# init hall_last_val:
sleep(1)
hall_vals = []
while len(hall_vals) < 1000:
    hall_vals.append(hall.read())

hall_last_val = avg(hall_vals)
print("init hall val:", hall_last_val)

while True:
    #print("read_u16:\t",65535-hall.read_u16())
    #print("read_uv:\t",hall.read_uv())
    #print(hall.read_uv()/1000000)
    #pwm_freq = map_value(potent_val, 0, 4095,0, 1023)
    #print(pwm_freq)
    read_encoder()
    hall_vals.pop(0)
    hall_vals.append(hall.read())
    hall_vals_avg = avg(hall_vals)
    
    if hall_vals_avg > (hall_last_val + 10) or hall_vals_avg < (hall_last_val - 10):
        hall_last_val = hall_vals_avg
        print("new hall value:", hall_vals_avg)
    #print(hall.read())
    #print("\t\t",hall.read())
    #print(dig.value())
    sleep(0.01)


