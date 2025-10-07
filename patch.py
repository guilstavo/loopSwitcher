from typing import List, Optional
from file import Json
from loop import Looper, Loop
from display import Display


class Patch:
    name: str
    looper: Looper
    active: bool = False

    def __init__(self, name: str, looper:Looper, loopStatusList: List[int], switchStatusList: List[int], active: bool = False):
        self.name = name
        self.active = active
        self.looper = looper

        print(f'Init Patch {self.name} with loops: ')

        i = 0
        for loop in self.looper.get_loops():
            loop.active = loopStatusList[i] == 1
            i += 1
            print(f'  Loop {loop.name} active: {loop.active}')

        i = 0
        for switch in self.looper.get_footswitch():
            switch.active = switchStatusList[i] == 1
            i += 1
            print(f'  Switch {switch.name} active: {switch.active}')


    def select(self):
        for loop in self.looper.get_loops():
            if loop.active:
                loop.activate()
            else:
                loop.deactivate()
        
        for switch in self.looper.get_footswitch():
            if switch.active:
                switch.activate()
            else:
                switch.deactivate
        

    def activate(self, file: Json, index: int):
        self.active = True
        file.save_to_file("active_patch_index", index)

    def deactivate(self):
        self.active = False

class Bank:

    name: str
    patches: List[Patch] = [] * 3
    active: bool = False
    
    def __init__(self, name: str, patches: List[Patch], active: bool = False):
        self.name = name
        self.patches = patches
        self.active = active

    def activate(self, file: Json, index: int):
        self.active = True
        file.save_to_file("active_bank_index", index)

    def deactivate(self):
        self.active = False

    def get_patch_by_index(self, index: int) -> Optional[Patch]:
        return self.patches[index]
    
    def get_active_patch(self) -> Optional[Patch]:
        return next((patch for patch in self.patches if patch.active), None)
    

class BankManager:
    banks: List[Bank] = []
    display = Display()
    statusFile: Json

    active_bank_name: str = ""
    active_patch_name: str = ""

    def __init__(self):
        self.banks = []
        self.file = Json()
        self.statusFile: Json = Json('active_status.json')

        active_bank_index = self.get_active_bank_index()
        active_patch_index = self.get_active_patch_index()

        for bank_index, bank_data in enumerate(self.file.data.get("banks", [])):
            print(f"Index: {bank_index}, Bank Data: {bank_data}")

            patches = []
            for patch_index, patch_data in enumerate(bank_data.get("patches", [])):
                patch = Patch(
                    name = patch_data.get("name", ""),
                    looper = Looper(), 
                    loopStatusList = patch_data.get("loops", []),
                    switchStatusList= patch_data.get("footswitch", []),
                    active = (bank_index == active_bank_index and patch_index == active_patch_index)
                )
                if patch.active:
                    patch.select()
                    self.set_active_patch_name(patch)
                patches.append(patch)
            bank = Bank(
                name = bank_data.get("name", ""),
                patches = patches,
                active = (bank_index == active_bank_index)
            )
            if bank.active:
                self.set_active_bank_name(bank.name)
            self.banks.append(bank)

    def get_active_bank_index(self) -> int: 
        return self.statusFile.data.get("active_bank_index", 0)
        
    def get_active_patch_index(self) -> int:
        return self.statusFile.data.get("active_patch_index", 0)

    def get_active_bank(self) -> Optional[Bank]:
        return next((bank for bank in self.banks if bank.active), None)
    
    def get_banks_count(self) -> int:
        return len(self.banks)

    def move_up_bank(self) -> Optional[Bank]:
        current_index = next((i for i, bank in enumerate(self.banks) if bank.active), None)
        if current_index is None:
            return
        
        self.banks[current_index].deactivate()
        new_bank_index = current_index + 1
        if new_bank_index >= len(self.banks):
            new_bank_index = 0
        self.set_active_bank(self.banks[new_bank_index], new_bank_index)
        return self.banks[new_bank_index]

    def move_down_bank(self) -> Optional[Bank]:
        current_index = next((i for i, bank in enumerate(self.banks) if bank.active), None)
        if current_index is None:
            return
        
        self.banks[current_index].deactivate()
        new_bank_index = current_index - 1
        if new_bank_index < 0:
            new_bank_index = len(self.banks) - 1
        self.set_active_bank(self.banks[new_bank_index], new_bank_index)
        return self.banks[new_bank_index]

    def select_patch(self, patch_index: int) -> Optional[Patch]:
        current_bank = self.get_active_bank()
        if current_bank:
            current_patch = current_bank.get_active_patch()
            new_patch = current_bank.get_patch_by_index(patch_index)
    
            if new_patch:
                new_patch.select()
                if current_patch:
                    current_patch.deactivate()
            
                self.set_active_patch(new_patch, patch_index)
                return new_patch


    def set_active_bank(self, bank: Bank, new_bank_index: int):
        bank.activate(self.statusFile, new_bank_index)
        self.set_active_bank_name(bank.name)

    def set_active_bank_name(self, active_bank_name):
        self.active_bank_name = active_bank_name
        self.display.print(active_bank_name)

    def get_active_bank_name(self) -> str:
        return self.active_bank_name or ""
    
    def set_active_patch(self, patch: Patch, new_patch_index: int):
        patch.activate(self.statusFile, new_patch_index)
        self.set_active_patch_name(patch)
    
    def set_active_patch_name(self, active_patch: Patch):
        self.active_patch_name = active_patch.name
        self.display.print(self.get_active_bank_name(), active_patch.name, self.display_loops(active_patch.looper.get_loops()), self.display_loops(active_patch.looper.get_footswitch(), True))
    
    def get_active_patch_name(self) -> str:
        return self.active_patch_name or ""
    
    def get_active_patch(self) -> Optional[Patch]:
        current_bank = self.get_active_bank()
        if current_bank:
            return current_bank.get_active_patch()
        return None
    
    def display_loops(self, loops: List[Loop], display_letter: Optional[bool]=None) -> str:
        line = ""
        for loop in loops:
            if display_letter is not None and display_letter:
                line += loop.name[0].upper()
            line += self.display.on_loop if loop.active else self.display.off_loop

        return line
    