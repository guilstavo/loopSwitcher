import time
import network
import socket
import re
from loop import Loop
from file import Html, Json
from typing import Optional

class WebServer():
    
    def __init__(self, config_file_name: str = "network_config.json"):
        config_data = Json(config_file_name).data 
        self.access_point = config_data.get("access_point", False)
        self.html = Html("index.html").data

        if (self.access_point):
            self.access_point_setup(config_data)
        else:
            self.connect(config_data)
        
        self.connection = self.open_socket()
        

    # this function connects the pico to a wifi network
    def connect(self, config_data):
        ssid = config_data.get("ssid")
        password = config_data.get("password")
        print("Connecting to network:", ssid)

        ip = config_data.get("ip")
        subnet = config_data.get("subnet")
        gateway = config_data.get("gateway")
        dns = config_data.get("dns")
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print("Current network config:", wlan.ifconfig())
        
        # Set the static IP configuration before connecting
        wlan.ifconfig((ip, subnet, gateway, dns))
        
        wlan.connect(ssid, password)
        while wlan.isconnected() == False:
            print("Connecting, please wait...")
            time.sleep(1)
        
        print("Connected! Network configuration:")
        print("IP:", wlan.ifconfig()[0])
        print("Subnet:", wlan.ifconfig()[1])
        print("Gateway:", wlan.ifconfig()[2])
        print("DNS:", wlan.ifconfig()[3])


    # you can call this function to make the pico host its own wifi AP instead
    def access_point_setup(self, config_data):
        ap_ssid = config_data.get("ap_ssid")
        ap_password = config_data.get("ap_password")
        # Sets up wireless module instance, configures access point, then turns on Wi-Fi hardware
        ap = network.WLAN(network.AP_IF)
        ap.config(ssid=ap_ssid, password=ap_password)
        ap.active(True)
        # We print the status of the connection here to help see whats going on
        while ap.active() == False:
            print("Initialising access point...")
            time.sleep(1)
            
        # Once it completes the while true loop, we will print out the Pico's IP on the network, will default to 192.168.4.1
        print("AP is operational, ip = ", ap.ifconfig()[0])

    # function to open a socket which is what the pico uses to allow other devices to send and recieve information with.
    def open_socket(self):
        # gets adress information for the socket, create a socket, bind it, then start listening for any clients trying to connect
        address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(address)
        s.listen(1)
        print("listening on", address)
        # then we will return this socket so we can use it in our main section
        return (s)
    
    # def webpage(self):
    def webpage(self, active_bank: str, active_patch: str, loops: list[Loop]):
        page = WebPage(active_bank, active_patch, loops)
        return page.render()

        
    def serve(self, active_bank: str, active_patch: str, loops: list[Loop] = []) -> Optional[str]:
        print('Start web server')
        # Start web server
        try:
            client = self.connection.accept()[0]
            request = client.recv(1024)
            request = str(request)
            # print("Request:", request)
            
            try:
                method = request.split()[0]
                print('method', method)
                path = request.split()[1]
            except IndexError:
                pass
            
            if method == "b'POST":
                mybytes = client.recv(1024)
                request = mybytes.decode('UTF-8')
                requestValue = request.split()[0]
                print('requestValue POST', requestValue)
                
            elif method == 'GET':
                try:
                    path = path.split('?')[0]
                    print(path)
                except IndexError:
                    pass
            
            html = self.webpage(active_bank, active_patch, loops)
            client.send("HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n")
            client.send(html)
            client.close()
            return requestValue
        
        except Exception as e:
            # Log the error and continue
            print(f"Error: {e}")

   
class WebPage:

    active_bank: str = ""
    active_patch: str = ""
    loop1: str = "disabled"
    loop2: str = "disabled"
    loop3: str = "disabled"
    loop4: str = "disabled"
    loop5: str = "disabled"
    loop6: str = "disabled"
    loop7: str = "disabled"
    loop8: str = "disabled"


    def __init__(self, active_bank: str, active_patch: str, loops: list[Loop] = []):
        self.active_bank = active_bank
        self.active_patch = active_patch
        
        if len(loops) > 0:
            self.loop1 = "enabled" if loops[0].active else "disabled"
        if len(loops) > 1:
            self.loop2 = "enabled" if loops[1].active else "disabled"
        if len(loops) > 2:
            self.loop3 = "enabled" if loops[2].active else "disabled"
        if len(loops) > 3:
            self.loop4 = "enabled" if loops[3].active else "disabled"
        if len(loops) > 4:
            self.loop5 = "enabled" if loops[4].active else "disabled"
        if len(loops) > 5:
            self.loop6 = "enabled" if loops[5].active else "disabled"
        if len(loops) > 6:
            self.loop7 = "enabled" if loops[6].active else "disabled"
        if len(loops) > 7:
            self.loop8 = "enabled" if loops[7].active else "disabled"

    def render(self) -> str:
        html = Html("index.html").data
        html = re.sub(r'<% bank %>', self.active_bank, html)
        html = re.sub(r'<% patch %>', self.active_patch, html)
        html = re.sub(r'<% loop1 %>', self.loop1, html)
        html = re.sub(r'<% loop2 %>', self.loop2, html)
        html = re.sub(r'<% loop3 %>', self.loop3, html)
        html = re.sub(r'<% loop4 %>', self.loop4, html)
        html = re.sub(r'<% loop5 %>', self.loop5, html)
        html = re.sub(r'<% loop6 %>', self.loop6, html)
        html = re.sub(r'<% loop7 %>', self.loop7, html)
        html = re.sub(r'<% loop8 %>', self.loop8, html)
        #         """
        # return the webpage as a string so we can serve it in our main section
        return str(html)