import time
import network
import socket
import re
from file import Html, Json

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
    def webpage(self, active_bank: str, active_patch: str):
        html = Html("index.html").data
        html = re.sub(r'<% bank %>', active_bank, html)
        html = re.sub(r'<% patch %>', active_patch, html)
        #         """
        # return the webpage as a string so we can serve it in our main section
        return str(html)

        
    def serve(self, active_bank: str, active_patch: str):
        # Start web server
        try:
            client = self.connection.accept()[0]
            request = client.recv(1024)
            request = str(request)
            
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
                
            elif method == 'GET':
                try:
                    path = path.split('?')[0]
                    print(path)
                except IndexError:
                    pass
            
            html = self.webpage(active_bank, active_patch)
            client.send("HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n")
            client.send(html)
            client.close()
            return requestValue
        
        except Exception as e:
            # Log the error and continue
            print(f"Error: {e}")

   