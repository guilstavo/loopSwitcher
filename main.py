import time
from patch import BankManager

bankManager = BankManager()


while True:

    bankManager.select_patch(0)
    time.sleep(3)
    bankManager.select_patch(1)
    time.sleep(3)
    bankManager.select_patch(2)
    time.sleep(3)
    bankManager.move_down_bank()
