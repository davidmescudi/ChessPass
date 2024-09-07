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
        
        # Send the commands required to initialize the display (based on the Waveshare documentation)
        ## Booster soft start
        self.send_command(0x06)
        self.send_data(0x17)  # A parameter to optimize the display
        self.send_data(0x17)
        self.send_data(0x17)

        ## Power settings
        self.send_command(0x01)  # Power Setting
        self.send_data(0x03)  # Source driving voltage
        self.send_data(0x00)  # Gate driving voltage
        self.send_data(0x2B)  # Source-Gate ON/OFF Period
        self.send_data(0x2B)

        ## Power on
        self.send_command(0x04)
        self.wait_until_idle()  # Wait until the display is ready

        ## Panel setting
        self.send_command(0x00)
        self.send_data(0xCF)  # KW-BF for A/C, BWROTP for B/W/R three-color mode

        ## VCOM and data interval setting
        self.send_command(0x50)
        self.send_data(0x37)

        ## Resolution setting
        self.send_command(0x61)  # Set Resolution
        self.send_data(0x128)  # 296 pixels
        self.send_data(0x00)
        self.send_data(0x80)   # 128 pixels

        ## VCM DC setting
        self.send_command(0x82)  # VCOM Voltage
        self.send_data(0x12)  # VCOM 1.2V

        ## Partial display setting
        self.send_command(0x30)  # PLL Control
        self.send_data(0x29)
        
        print("E-ink display initialized successfully.")

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

    def wait_until_idle(self):
        # Check the busy pin and wait until the display is ready
        print("Waiting for display to be idle...")
        while self.is_busy():
            time.sleep(0.1)
        print("Display is ready.")

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
