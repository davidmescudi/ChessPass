from machine import Pin, ADC
from time import sleep

# magnet = Pin(2, Pin.OUT)
# magnet.on()
#hall = ADC(Pin(3)) 
#hall.atten(ADC.ATTN_11DB)
pins = [36, 39, 34, 35, 32, 33, 25, 26, 27]
# ADCs = [ADC(Pin(x)) for x in pins]
# set attenuation
#for adc in ADCs:
 #   adc.atten(ADC.ATTN_11DB)

pin = pins[3]
hall = ADC(Pin(pin, Pin.IN))
hall.atten(ADC.ATTN_11DB)
#dig = Pin(6, Pin.IN)
#potent = ADC(Pin(4))

avg = hall.read()
min_val = avg
max_val = avg

for _ in range(20000):
    val = hall.read()
    avg += val
    avg = avg // 2
    min_val = min(min_val, val)
    max_val = max(max_val, val)

print("avg:", avg)
print("min:", min_val)
print("max:", max_val)
while False:
    #print("read_u16:\t",65535-hall.read_u16())
    #print("read_uv:\t",hall.read_uv())
    #print(hall.read_uv()/1000000)
    #pwm_freq = map_value(potent_val, 0, 4095,0, 1023)
    #print(pwm_freq)
    #for i, adc in enumerate(ADCs):
     #   print(f"Hall sensor {i}: {adc.read()}")
    #print(f"Hall sensor {pin}:", hall.read())
    #if len(readings)
    #print(dig.value())
    pass
    

