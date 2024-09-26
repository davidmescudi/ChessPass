from machine import Pin, ADC
from time import sleep

# magnet = Pin(2, Pin.OUT)
# magnet.on()
#hall = ADC(Pin(3)) 
#hall.atten(ADC.ATTN_11DB)
pins = [36, 39, 34, 35, 32, 33, 25, 26, 27]
ADCs = [ADC(Pin(x)) for x in pins]
# set attenuation
for adc in ADCs:
    adc.atten(ADC.ATTN_11DB)
    
#hall = Pin(3, Pin.IN)
#dig = Pin(6, Pin.IN)
#potent = ADC(Pin(4))

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

while True:
    #print("read_u16:\t",65535-hall.read_u16())
    #print("read_uv:\t",hall.read_uv())
    #print(hall.read_uv()/1000000)
    #pwm_freq = map_value(potent_val, 0, 4095,0, 1023)
    #print(pwm_freq)
    for i, adc in enumerate(ADCs):
        print(f"Hall sensor {i}: {adc.read()}")
    #print("\t\t",hall.read())
    #print(dig.value())
    sleep(0.5)

