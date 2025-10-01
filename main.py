from patch import BankManager
from machine import reset
from web_server import WebServer

# bankManager = BankManager()

# def switch(request):
#     if request == "bank=up":
#         bankManager.move_up_bank()
#         return "Bank Up"
#     elif request == "bank=down":
#         bankManager.move_down_bank()
#         return "Bank Down"
#     elif request == "patch=1":
#         bankManager.select_patch(0)
#         return "Select patch 1"
#     elif request == "patch=2":
#         bankManager.select_patch(1)
#         return "Select patch 2"
#     elif request == "patch=3":
#         bankManager.select_patch(2)
#         return "Select patch 3"
#     else:
#         return "no match"

# try:
#     webServer = WebServer("network_config.json")
#     while True:
#         requestValue = webServer.serve(active_bank=bankManager.get_active_bank_name(), active_patch=bankManager.get_active_patch_name())
#         print('requestValue main.py', switch(requestValue))
# except KeyboardInterrupt:
#     reset()
