"""
MicroPython Nokia 5110 PCD8544 84x48 LCD driver
https://github.com/mcauser/micropython-pcd8544

MIT License
Copyright (c) 2016-2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
from ustruct import pack
from utime import sleep_us
import framebuf
from machine import SPI, Pin

# Function set 0010 0xxx
FUNCTION_SET     = const(0x20)
POWER_DOWN       = const(0x04)
ADDRESSING_VERT  = const(0x02)
EXTENDED_INSTR   = const(0x01)

# Display control 0000 1x0x
DISPLAY_BLANK    = const(0x08)
DISPLAY_ALL      = const(0x09)
DISPLAY_NORMAL   = const(0x0c)
DISPLAY_INVERSE  = const(0x0d)

# Temperature control 0000 01xx
TEMP_COEFF_0     = const(0x04)
TEMP_COEFF_1     = const(0x05)
TEMP_COEFF_2     = const(0x06) # default
TEMP_COEFF_3     = const(0x07)

# Bias system 0001 0xxx
BIAS_1_100       = const(0x10)
BIAS_1_80        = const(0x11)
BIAS_1_65        = const(0x12)
BIAS_1_48        = const(0x13)
BIAS_1_40        = const(0x14) # default
BIAS_1_24        = const(0x15)
BIAS_1_18        = const(0x16)
BIAS_1_10        = const(0x17)

# Set operation voltage
SET_VOP          = const(0x80)

# DDRAM addresses
COL_ADDR         = const(0x80) # x pos (0~83)
BANK_ADDR        = const(0x40) # y pos, in banks of 8 rows (0~5)

# Display dimensions
WIDTH            = const(0x54) # 84
HEIGHT           = const(0x30) # 48

# Custom byte array
CHESS_PASS_LOGO = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xfc<\x00\x00\x00\x00\x00\x00\x00\x03\xf7\xe4<\x00\x00\x00\x00\x00\x00\x00\x07>\xc6<\x00\x00\x00\x00\x00\x00\x00\x0c\xc3\xc4<\x00\x00\x00\x00\x00\x00\x00\x19?\xe6<\x00\x00\x00\x00\x00\x00\x00\x10\xff\xc28\x00\x00\x00\x00\x00\x00\x00!\xff\xc6<@\x01@\x07\xc0>\x00#\xf7\xe4=\xf8\x07\xf0\x12\xf0K\x80c\xc0:?\xfc\x0f\xf8\x07\xe8\xbf`#\x80\x00?\xfe\x1f|.\xc87\x00G\xc0\x00>><\x1e\x0c\x11`@c\x80\x00<\x1e8\x1e\x06\x000\x00#\xc0|<\x1e\x7f\xfe\x1b\xd0\xbe\x80#\xff\xc6<\x1e\x7f\xff\r\xd0n\x801\xff\xc6<\x0e\x7f\xfe\x07\x90>\x80\x10\xff\xe4<\x1e8\x00\x00\xe0\x06\x80\x19?\xc6<\x1e<\x00P\xd2\x86\x00\x0c\xd2\xc48\x1e?<]\xc2n\x80\x07-\xe6<\x0e\x1f\xfc_\x82\xfc\x00\x03\xff\xc4<\x1e\x07\xf8Z!\xe9\x00\x00\x7f\xfa4\x0c\x03\xd0\x0f\x80<\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00-@\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00<\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00<\x1e\x00\x00\x00\x00\x00\x00\x00\x00\x00<\x0f\x02\x00\x03\x80<\x00\x00\x00\x00<\x1e\x0f\xee\txK\x80\x00\x00\x00<\x1f\x1f\xfe\x07\xf4\xbf \x00\x00\x00<>?\xfe\x16\xe47@\x00\x00\x00?\xfc|~\x06\x14a@\x00\x00\x00?\xf8x\x1e\x16\x00\xb0\x00\x00\x00\x00?\xe0x\x1f\x13\xc0\xbe\x00\x00\x00\x00<\x00x\x0e\x0f\xe8^\x80\x00\x00\x00<\x00x\x1e\x02\xc8:\x80\x00\x00\x00<\x00x\x1e\x00\xf0\x06\x80\x00\x00\x00<\x00|\x1e \xc2\x06\x80\x00\x00\x00<\x00>\xfeL\xd2\xe6\x00\x00\x00\x00<\x00?\xfe_\xc2\xfc\x80\x00\x00\x00<\x00\x0f\xfe]\x12\xd9\x00\x00\x00\x00<\x00\x07\x8e\x07\xc0~\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

class DISPLAY:
	def __init__(self, spi, cs, dc, bl, rst=None):
		self.spi    = spi
		self.cs     = cs   # chip enable, active LOW
		self.dc     = dc   # data HIGH, command LOW
		self.rst    = rst  # reset, active LOW
		self.bl 	= bl   # backlight
		
		self.height = HEIGHT  # For Writer class
		self.width = WIDTH

		self.cs.init(self.cs.OUT, value=1)
		self.dc.init(self.dc.OUT, value=0)

		if self.rst:
			self.rst.init(self.rst.OUT, value=1)
		self.reset()
		self.init()

	def init(self, horizontal=True, contrast=0x3f, bias=BIAS_1_40, temp=TEMP_COEFF_2):
		# power up, horizontal addressing, basic instruction set
		self.fn = FUNCTION_SET
		self.addressing(horizontal)
		self.contrast(contrast, bias, temp)
		self.cmd(DISPLAY_NORMAL)
		self.clear()

	def reset(self):
		# issue reset impulse to reset the display
		# you need to call power_on() or init() to resume
		self.rst(1)
		sleep_us(100)
		self.rst(0)
		sleep_us(100) # reset impulse has to be >100 ns and <100 ms
		self.rst(1)
		sleep_us(100)

	def power_on(self):
		self.cs(1)
		self.fn &= ~POWER_DOWN
		self.cmd(self.fn)

	def power_off(self):
		self.fn |= POWER_DOWN
		self.cmd(self.fn)

	def contrast(self, contrast=0x3f, bias=BIAS_1_40, temp=TEMP_COEFF_2):
		for cmd in (
			# extended instruction set is required to set temp, bias and vop
			self.fn | EXTENDED_INSTR,
			# set temperature coefficient
			temp,
			# set bias system (n=3 recommended mux rate 1:40/1:34)
			bias,
			# set contrast with operating voltage (0x00~0x7f)
			# 0x00 = 3.00V, 0x3f = 6.84V, 0x7f = 10.68V
			# starting at 3.06V, each bit increments voltage by 0.06V at room temperature
			SET_VOP | contrast,
			# revert to basic instruction set
			self.fn & ~EXTENDED_INSTR):
			self.cmd(cmd)

	def invert(self, invert):
		self.cmd(DISPLAY_INVERSE if invert else DISPLAY_NORMAL)

	def clear(self):
		# clear DDRAM, reset x,y position to 0,0
		self.data([0] * (HEIGHT * WIDTH // 8))
		self.position(0, 0)

	def addressing(self, horizontal=True):
		# vertical or horizontal addressing
		if horizontal:
			self.fn &= ~ADDRESSING_VERT
		else:
			self.fn |= ADDRESSING_VERT
		self.cmd(self.fn)

	def position(self, x, y):
		# set cursor to column x (0~83), bank y (0~5)
		self.cmd(COL_ADDR | x)  # set x pos (0~83)
		self.cmd(BANK_ADDR | y) # set y pos (0~5)

	def cmd(self, command):
		self.dc(0)
		self.cs(0)
		self.spi.write(bytearray([command]))
		self.cs(1)

	def data(self, data):
		self.dc(1)
		self.cs(0)
		self.spi.write(pack('B'*len(data), *data))
		self.cs(1)


class DISPLAY_FRAMEBUF(DISPLAY):
	def __init__(self, spi, cs, dc, bl, rst=None):
		initialised_spi = SPI(spi)
		initialised_spi.init(baudrate=2000000, polarity=0, phase=0)
		super().__init__(initialised_spi, Pin(cs), Pin(dc), Pin(bl, Pin.OUT, value=0), Pin(rst))
		self.buf = bytearray((HEIGHT // 8) * WIDTH)
		self.fbuf = framebuf.FrameBuffer(self.buf, WIDTH, HEIGHT, framebuf.MONO_VLSB)

	def fill(self, col):
		self.fbuf.fill(col)

	def pixel(self, x, y, col):
		self.fbuf.pixel(x, y, col)

	def scroll(self, dx, dy):
		self.fbuf.scroll(dx, dy)
		# software scroll

	def text(self, string, x, y, col):
		self.fbuf.text(string, x, y, col)

	def line(self, x1, y1, x2, y2, col):
		self.fbuf.line(x1, y1, x2, y2, col)

	def hline(self, x, y, w, col):
		self.fbuf.hline(x, y, w, col)

	def vline(self, x, y, h, col):
		self.fbuf.vline(x, y, h, col)

	def rect(self, x, y, w, h, col):
		self.fbuf.rect(x, y, w, h, col)

	def fill_rect(self, x, y, w, h, col):
		self.fbuf.fill_rect(x, y, w, h, col)
	
	def showLogo(self):
		self.fbuf.fill(0)
		logo_buf = framebuf.FrameBuffer(CHESS_PASS_LOGO, WIDTH, HEIGHT, framebuf.MONO_HLSB)
		self.blit(logo_buf, 0, 0, 0)
		self.clear()
		self.data(self.buf)

	def showActiveFigures(self):
		self.fbuf.fill(0)
		self.text("Test", 20, 20, 0)

	def blit(self, fbuf, position_x, position_y, rotation = 0):
		self.fbuf.blit(fbuf, position_x, position_y, rotation)

	def show(self):
		self.data(self.buf)
