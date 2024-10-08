from lib.uQR import QRCode
from lib.config import DISPLAY_PINS
from lib import DISPLAY_FRAMEBUF

display = DISPLAY_FRAMEBUF(
    DISPLAY_PINS["SPI"],
    DISPLAY_PINS["CS"],
    DISPLAY_PINS["DC"],
    DISPLAY_PINS["BL"],
    DISPLAY_PINS["RST"],
)

qr = QRCode(border=3)
qr.add_data('https://is.gd/u1TXB0')
matrix = qr.get_matrix()
x_offset = 18
scaling = 1.5
display.power_on()
for y in range(len(matrix)*scaling): # Scaling the bitmap by 2
     for x in range(len(matrix[0])*scaling): # because my screen is tiny.
         value = not matrix[int(y/scaling)][int(x/scaling)] # Inverting the values because
         display.pixel(x+x_offset,y,value) # black is `True` in the matrix.
display.show()                                    
