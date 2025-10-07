from patch import BankManager, Patch
from machine import reset
from web_server import WebServer
from typing import Optional

bankManager = BankManager()
currentPatch: Optional[Patch] = bankManager.get_active_patch()

def switch(request: Optional[str], currentPatch: Optional[Patch]) -> Optional[Patch]:
    if request is None:
        return currentPatch
    
    if request == "bank=up":
        bankManager.move_up_bank()
        return currentPatch
    elif request == "bank=down":
        bankManager.move_down_bank()
        return currentPatch
    elif request == "patch=1":
        return bankManager.select_patch(0)
    elif request == "patch=2":
        return bankManager.select_patch(1)
    elif request == "patch=3":
        return bankManager.select_patch(2)
    elif request == "patch=4":
        return bankManager.select_patch(3)
    else:
        return None


webServer = WebServer("network_config.json")
while True:
    if currentPatch is None:
        requestValue = webServer.serve(active_bank=bankManager.get_active_bank_name(), active_patch=bankManager.get_active_patch_name())
    else:
        requestValue = webServer.serve(active_bank=bankManager.get_active_bank_name(), active_patch=bankManager.get_active_patch_name(), loops=currentPatch.looper.get_loops(), footswitch=currentPatch.looper.get_footswitch(), midi_program=currentPatch.midiPresets[0].program)
    
    currentPatch = switch(requestValue, currentPatch)
