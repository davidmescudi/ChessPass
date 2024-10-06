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

qr = QRCode()
qr.add_data('uQR rocks!')
matrix = qr.get_matrix()
print(matrix)

display.power_on()
for y in range(len(matrix)*2): # Scaling the bitmap by 2
     for x in range(len(matrix[0])*2): # because my screen is tiny.
         value = not matrix[int(y/2)][int(x/2)] # Inverting the values because
         display.pixel(x,y,value) # black is `True` in the matrix.
display.show()                                    