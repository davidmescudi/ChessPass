from machine import Pin, SPI
import time

class EinkDisplay:
    def __init__(self, spi_bus=1, cs_pin=15, dc_pin=4, rst_pin=16, busy_pin=17, sck_pin=18, mosi_pin=23):
        # Initialize the SPI bus and the relevant pins for the e-ink display
        self.spi = SPI(spi_bus, baudrate=2000000, polarity=0, phase=0, sck=Pin(sck_pin), mosi=Pin(mosi_pin))
        self.cs = Pin(cs_pin, Pin.OUT)
        self.dc = Pin(dc_pin, Pin.OUT)
        self.rst = Pin(rst_pin, Pin.OUT)
        self.busy = Pin(busy_pin, Pin.IN)

        # Set the initial state of the pins and initialize the display
        self.init_display()

    def init_display(self):
        # Reset the display and send necessary initialization commands
        self.reset()
        print("Initializing e-ink display...")

        # Here you would send specific initialization commands to the e-ink display
        # Example: self.send_command(some_command)
        # Refer to your specific display's datasheet for required commands

    def reset(self):
        # Reset the e-ink display using the reset (RST) pin
        self.rst.value(1)
        time.sleep(0.1)
        self.rst.value(0)
        time.sleep(0.1)
        self.rst.value(1)
        print("E-ink display reset")

    def send_command(self, command):
        # Send a command to the e-ink display
        self.cs.value(0)
        self.dc.value(0)  # Set DC pin to 0 for command mode
        self.spi.write(bytearray([command]))
        self.cs.value(1)

    def send_data(self, data):
        # Send data to the e-ink display
        self.cs.value(0)
        self.dc.value(1)  # Set DC pin to 1 for data mode
        self.spi.write(bytearray([data]))
        self.cs.value(1)

    def is_busy(self):
        # Check if the e-ink display is busy
        return self.busy.value() == 1

    def show_menu(self, menu_items, selected_index):
        # Show the menu on the e-ink display (this method simulates a menu display)
        if self.is_busy():
            print("E-ink display is busy, waiting...")
            return
        if self.needs_refresh:
            print("Updating e-ink display:")
            for i, item in enumerate(menu_items):
                if i == selected_index:
                    print(f"> {item}")  # Indicate selected item
                else:
                    print(f"  {item}")
            self.refresh_display()
        else:
            print("No update needed.")

    def refresh_display(self):
        # Simulate the refresh process of the e-ink display
        print("Refreshing e-ink display...")
        time.sleep(1)  # Simulate slow refresh rate
        self.needs_refresh = False

    def mark_for_refresh(self):
        # Mark the display for refresh
        self.needs_refresh = True
