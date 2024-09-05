# main.py
from machine import Timer
from lib.display import EinkDisplay
from lib.buttons import Button
from lib.sensors import HallSensor
from lib.menu import Menu
import time

# Callback functions for button press
def on_up_button():
    menu.navigate_up()

def on_down_button():
    menu.navigate_down()

def on_select_button():
    if time.ticks_diff(time.ticks_ms(), select_button.last_press) > 1000:
        menu.go_back()  # Long press action (go back)
    else:
        menu.select()  # Short press action (select)

# Initialize the display with default pins or pass custom pin numbers
display = EinkDisplay()
menu = Menu(display)

up_button = Button(pin_num=13, callback=on_up_button)
down_button = Button(pin_num=14, callback=on_down_button)
select_button = Button(pin_num=15, callback=on_select_button)

# Hall sensor initialization
hall_sensors = [HallSensor(pin_num) for pin_num in [32, 33, 34, 35, 36, 39, 25, 26, 27]]

# Read Hall sensor values continuously in the background
def read_hall_sensors(timer):
    sensor_values = [sensor.read_value() for sensor in hall_sensors]
    print(f"Hall sensor readings: {sensor_values}")

# Setup a timer to read hall sensors every 500ms
hall_timer = Timer(0)
hall_timer.init(period=500, mode=Timer.PERIODIC, callback=read_hall_sensors)

# Main loop
def main():
    menu.update_display()  # Show the initial menu
    while True:
        # Check button presses
        up_button.check_pressed()
        down_button.check_pressed()
        select_button.check_pressed()

        # Update display only if a refresh is needed
        if display.needs_refresh:
            menu.update_display()

        time.sleep(0.1)  # Small delay for debouncing

if __name__ == "__main__":
    main()
