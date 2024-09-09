# *****************************************************************************
# * | File        :	  Pico_ePaper-2.9-B.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-03-16
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

# Pin definitions
RST_PIN         = 16
DC_PIN          = 4
CS_PIN          = 15
BUSY_PIN        = 17

# Bytecode descriptions
PANEL_SETTING                   = 0x00
POWER_SETTING                   = 0x01
POWER_OFF                       = 0x02
POWER_ON                        = 0x04
BOOSTER_SOFT_START              = 0x06
DEEP_SLEEP                      = 0x07
DATA_START_TRANSMISSION_1       = 0x10
DISPLAY_REFRESH                 = 0x12
DATA_START_TRANSMISSION_2       = 0x13
VCOM_AND_DATA_INTERVAL_SETTING  = 0x50
RESOLUTION_SETTING              = 0x61
GET_STATUS                      = 0x71
FILL                            = 0x00
WHITE							= 0xff

class EPD_2in9_B:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        print('busy')
        self.send_command(GET_STATUS)
        while self.digital_read(self.busy_pin) == 0:
            self.send_command(GET_STATUS)
            self.delay_ms(10)
        print('busy release')

    def TurnOnDisplay(self):
        self.send_command(DISPLAY_REFRESH)
        self.ReadBusy()

    def init(self):
        print('init')
        self.reset()
        self.send_command(POWER_ON)
        self.ReadBusy()  # Wait for the e-paper IC to release the idle signal

        self.send_command(PANEL_SETTING)  # Panel setting
        self.send_data(0x0f)              # LUT from OTP, 128x296
        self.send_data(0x89)              # Temperature sensor, boost, and timing settings

        self.send_command(RESOLUTION_SETTING)  # Set resolution
        self.send_data(0x80)                   # Width: 128
        self.send_data(0x01)                   # Height part 1: 296 (0x128 >> 8)
        self.send_data(0x28)                   # Height part 2: 296 (0x128 & 0xff)

        self.send_command(VCOM_AND_DATA_INTERVAL_SETTING)  # VCOM and data interval
        self.send_data(0x77)  # Set WBmode and WBRmode settings

        return 0

    def display(self):
        self.send_command(DATA_START_TRANSMISSION_1)  # Start sending black data
        self.send_data1(self.buffer_black)

        self.send_command(DATA_START_TRANSMISSION_2)  # Start sending red data
        self.send_data1(self.buffer_red)

        self.TurnOnDisplay()

    def Clear(self, colorblack, colorred):
        self.send_command(DATA_START_TRANSMISSION_1)
        self.send_data1([colorblack] * self.height * int(self.width / 8))

        self.send_command(DATA_START_TRANSMISSION_2)
        self.send_data1([colorred] * self.height * int(self.width / 8))

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(POWER_OFF)
        self.ReadBusy()
        self.send_command(DEEP_SLEEP)
        self.send_data(0xA5)  # Command to enter deep sleep

        self.delay_ms(2000)
        self.module_exit()


if __name__ == '__main__':
    epd = EPD_2in9_B()
    epd.Clear(WHITE, WHITE)

    epd.imageblack.fill(WHITE)
    epd.imagered.fill(WHITE)
    epd.imageblack.text("Waveshare", 0, 10, FILL)
    epd.imagered.text("ePaper-2.9-B", 0, 25, FILL)
    epd.imageblack.text("JOY -iT NodeMCU - ESP32", 0, 40, FILL)
    epd.imagered.text("Hello World", 0, 55, FILL)
    epd.display()
    epd.delay_ms(2000)

    epd.imagered.vline(10, 90, 40, FILL)
    epd.imagered.vline(90, 90, 40, FILL)
    epd.imageblack.hline(10, 90, 80, FILL)
    epd.imageblack.hline(10, 130, 80, FILL)
    epd.imagered.line(10, 90, 90, 130, FILL)
    epd.imageblack.line(90, 90, 10, 130, FILL)
    epd.display()
    epd.delay_ms(2000)

    epd.imageblack.rect(10, 150, 40, 40, FILL)
    epd.imagered.fill_rect(60, 150, 40, 40, FILL)
    epd.display()
    epd.delay_ms(2000)

    epd.Clear(WHITE, WHITE)
    epd.delay_ms(2000)
    print("sleep")
    epd.sleep()