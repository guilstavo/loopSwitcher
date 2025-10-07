from machine import UART, Pin

class Midi:
    
    uart: UART

    def __init__(self, tx_pin: int):
        self.uart = UART(1, baudrate=31250, tx=Pin(tx_pin))

    def send_pc(self, channel, program):
        status = 0xC0 | ((channel - 1) & 0x0F)
        self.uart.write(bytes([status, program & 0x7F]))

class Midi_preset:

    channel: int
    program: int

    def __init__(self, channel: int, program: int):
        self.channel = channel
        self.program = program