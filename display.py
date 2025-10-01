
from machine import Pin, SoftI2C
from lib_lcd1602_2004_with_i2c import LCD

class Display:
    
    def __init__(self, sclPin: int = 1, sdaPin: int = 0):
        
        self.lcd = LCD(SoftI2C(scl=Pin(sclPin), sda=Pin(sdaPin), freq=100000))
        print('Init Display')

    def print(self, line1: str = "", line2: str = "", line3: str = "", line4: str = ""):
        self.lcd.puts(line1, 0, 0)
        self.lcd.puts(line2, 1, 0)
        self.lcd.puts(line3, 2, 0)
        self.lcd.puts(line4, 3, 0)
        print('Display Print: ', line1, line2, line3, line4)
