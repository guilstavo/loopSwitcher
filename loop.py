from machine import Pin
from typing import List, Optional
from file import Json


# One Loop is each individual Send/Return input
class Loop:
    ACTIVE_PIN_VALUE: int = 1
    INACTIVE_PIN_VALUE: int = 0

    name: str
    pinSend: Pin
    pinReturn: Optional[Pin] = None
    active: bool = False
    order: int
    
    def __init__(self, name: str, pinIn: int, pinOut: Optional[int] = None):
        
        self.name = name
        self.pinSend = Pin(pinIn, Pin.OUT)
        self.order = pinIn

        if pinOut is not None:
            self.pinReturn = Pin(pinOut, Pin.OUT)
        
        self.deactivate()
        print('Init Loop', name)

    def activate(self):
        self.pinSend.value(self.ACTIVE_PIN_VALUE) 
        if self.pinReturn is not None:
            self.pinReturn.value(self.ACTIVE_PIN_VALUE)
        print(f'Loop {self.name} activated')

    def deactivate(self):
        self.pinSend.value(self.INACTIVE_PIN_VALUE) 
        if self.pinReturn is not None:
            self.pinReturn.value(self.INACTIVE_PIN_VALUE)
        print(f'Loop {self.name} deactivated')

    def get_css_class(self) -> str:
        return "enabled" if self.active else "disabled"

# Looper is the set of Loops (8 loops in total). 
# The Looper logic also includes the Footswitch, which is tecnically another set of loops
class Looper:
    
    def __init__(self, fileName: str = "config.json"):
        self.__loopers:List[Loop] = []
        self.__footSwitch:List[Loop] = []

        file = Json(fileName)
        for loop_data in file.data.get("loops", []):
            self.add_loop(
                name = loop_data.get("name"),
                pinIn = loop_data.get("pinSend"),
                pinOut = loop_data.get("pinReturn")
            )
        for switch_name, switch_pin in file.data.get("footswitch", {}).items():
            self.add_switch(
                name = switch_name,
                pin = switch_pin
            )

    def add_loop(self, name: str,  pinIn: int, pinOut: int):
        loop = Loop(name, pinIn, pinOut)
        self.__loopers.append(loop)
        print(f'Added loop {name} with pins {pinIn} and {pinOut}')

    def select_loop(self, loop_name: str) -> Optional[Loop]:
        for loop in self.__loopers:
            if loop.name == loop_name:
                return loop
        return None  # In case no loop is found
    
    def get_loops(self) -> List[Loop]:
        return self.__loopers

    def add_switch(self, name: str,  pin: int):
        switch = Loop(name=name, pinIn=pin)
        self.__footSwitch.append(switch)
        print(f'Added switch {name} with pin {pin}')

    def get_footswitch(self) -> List[Loop]:
        return sorted(self.__footSwitch, key=lambda x: x.order)