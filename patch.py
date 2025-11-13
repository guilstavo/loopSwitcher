from typing import List, Optional
from file import Json
from loop import Looper
from midi import Midi, Midi_preset

class Patch:
    name: str
    looper: Looper
    midiPresets: List[Midi_preset] = []
    midi: Midi
    active: bool = False

    def __init__(self, name: str, looper:Looper, loopStatusList: List[int], switchStatusList: List[int], midiPresetsConfigList: List, midiPin: int, active: bool = False):
        self.name = name
        self.active = active
        self.looper = looper
        self.midi = Midi(midiPin)
        self.midiPresets = []
        self.loopStatusList = list(map(bool, loopStatusList))
        self.switchStatusList = list(map(bool, switchStatusList))

        print(f'Init Patch {self.name}: ')

        for midiPresetConfig in midiPresetsConfigList:
            midiPreset = Midi_preset(channel=midiPresetConfig.get("channel"), program=midiPresetConfig.get("program"))
            self.midiPresets.append(midiPreset)
            print(f'  Midi Preset channel {midiPreset.channel} program: {midiPreset.program}')


    def select(self):
        for status, loop in zip(self.loopStatusList, self.looper.get_loops()):
            if status:
                loop.activate()
            else:
                loop.deactivate()

        for status, switch in zip(self.switchStatusList, self.looper.get_footswitch()):
            if status:
                switch.activate()
            else:
                switch.deactivate()

        for midiPreset in self.midiPresets:
            self.midi.send_pc(midiPreset.channel, midiPreset.program)

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
    