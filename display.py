# MicroPython SH1106 OLED driver
#
# Pin Map I2C for ESP8266
#   - 3v - xxxxxx   - Vcc
#   - G  - xxxxxx   - Gnd
#   - D2 - GPIO 5   - SCK / SCL
#   - D1 - GPIO 4   - DIN / SDA
#   - D0 - GPIO 16  - Res (required, unless a Hardware reset circuit is connected)
#   - G  - xxxxxx     CS
#   - G  - xxxxxx     D/C
#
# Pin's for I2C can be set almost arbitrary
#
from machine import Pin, I2C
import sh1106

class Display:
    
    def __init__(self, sclPin: int = 5, sdaPin: int = 4):
        
        i2c = I2C(scl=Pin(sclPin), sda=Pin(sdaPin), freq=400000)
        
        self.display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)
        
        self.display.sleep(False)
        print('Init Display')

    def print(self, text):
        self.display.fill(0)
        self.display.text(text, 0, 20, 2)
        self.display.show()
        print('Display Print: ', text)
