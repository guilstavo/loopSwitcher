from machine import Pin
from typing import List, Optional
from file import Json

class Loop:

    name: str
    pinSend: Pin
    pinReturn: Pin
    active: bool = False
    
    def __init__(self, name: str, pinIn: int, pinOut: int):
        
        self.name = name
        self.pinSend = Pin(pinIn, Pin.OUT)
        self.pinReturn = Pin(pinOut, Pin.OUT)
        
        self.deactivate()
        print('Init Loop')

    def activate(self):
        self.pinSend.value(1) 
        self.pinReturn.value(1)
        print(f'Loop {self.name} activated')

    def deactivate(self):
        self.pinSend.value(0) 
        self.pinReturn.value(0)
        print(f'Loop {self.name} deactivated')


class Looper:
    
    def __init__(self, fileName: str = "config.json"):
        self.__loopers:List[Loop] = []
        file = Json(fileName)
        for loop_data in file.data.get("loops", []):
            self.add_loop(
                name = loop_data.get("name", ""),
                pinIn = loop_data.get("pinSend", 0),
                pinOut = loop_data.get("pinReturn", 0)
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
    
    def loop_count(self) -> int:
        return len(self.__loopers)
    
    def clone(self):
        # Create a new Looper instance
        new_looper = Looper()
        # Copy attributes manually
        new_looper.__loopers = [loop for loop in self.__loopers]
        return new_looper