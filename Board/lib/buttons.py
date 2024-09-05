from machine import Pin
import time

class Button:
    def __init__(self, pin_num, callback):
        self.button = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.callback = callback
        self.last_press = time.ticks_ms()
        self.debounce_time = 200  # Debounce time in milliseconds

    def check_pressed(self):
        if self.button.value() == 0:  # Button pressed (active-low)
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_press) > self.debounce_time:
                self.callback()
                self.last_press = now
