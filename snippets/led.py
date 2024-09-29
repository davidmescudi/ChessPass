from machine import Pin
from time import sleep

led = Pin(32, Pin.OUT) # Attention pin 34 did not work

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)

