import time
import network
import socket
from loop import Loop
from file import Html, Json
from typing import Optional
import json

class WebServer():
    
    def __init__(self, config_file_name: str = "network_config.json"):
        config_data = Json(config_file_name).data 
        self.access_point = config_data.get("access_point", False)
        self.webPage = WebPage()

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
        try:
            s.bind(address)
            s.listen(1)
            print("listening on", address)
        except Exception as e:
            print("Socket error:", e)
        # then we will return this socket so we can use it in our main section
        return (s)

    def serve(self, active_bank: str, active_patch: str, loops: list[Loop] = [], footswitch: list[Loop] = [], midi_program: int = 0) -> Optional[str]:
        print('Start web server')
        try:
            requestValue = None
            client = self.connection.accept()[0]
            request = str(client.recv(1024))

            # Determine request path
            request_line = request.split('\r\n')[0]
            parts = request_line.split()
            path = parts[1] if len(parts) > 1 else "/"

            if "POST" in request:
                print('POST request')
                mybytes = client.recv(1024)
                request = mybytes.decode('UTF-8')
                requestParts = request.split()
                requestValue = requestParts[0] if requestParts else None
                print('requestValue POST', requestValue)

            # --- 🟢 1. If client requests /events → send SSE stream ---
            if path == "/events":
                print("SSE client connected")
                client.send(
                    'HTTP/1.1 200 OK\r\n'
                    'Content-Type: text/event-stream\r\n'
                    'Cache-Control: no-cache\r\n'
                    'Connection: keep-alive\r\n\r\n'
                )

                # Stream updates periodically
                for _ in range(120):  # 60 updates (~1 per sec)
    
                    context = {
                        "bank": active_bank,
                        "patch": active_patch,
                        "midi_program": midi_program,
                        "classes":{}
                    }

                    # add loops dynamically
                    for i, loop in enumerate(loops, start=1):
                        context["classes"][f"loop{i}_status"] = loop.get_css_class()
                        # context[f"loop{i}_name"] = loop.name

                    for i, switch in enumerate(footswitch, start=1):
                        context["classes"][f"switch{i}_status"] = switch.get_css_class()
                        # context[f"switch{i}_name"] = switch.name

                    msg = f"data: {json.dumps(context)}\n\n"
                    client.send(msg)
                    time.sleep(1)

                client.close()
                return None


            # client.close()
            html = self.webPage.render(active_bank, active_patch, loops, footswitch, midi_program)
            encoded = html.encode("utf-8")

            # Build proper HTTP response
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(encoded)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            # Encode headers
            header_bytes = response_headers.encode("utf-8")

            # Send headers first
            total_sent = 0
            while total_sent < len(header_bytes):
                sent = client.send(header_bytes[total_sent:])
                if sent == 0:
                    break
                total_sent += sent

            # Send body
            total_sent = 0
            while total_sent < len(encoded):
                sent = client.send(encoded[total_sent:])
                if sent == 0:
                    break
                total_sent += sent

            # Close client connection
            client.close()

            return requestValue

        except Exception as e:
            print(f"Error: {e}")
    

   
class WebPage:

    html: str

    def __init__(self):
        self.html = Html("index.html").data

    def render(self, active_bank: str, active_patch: str, loops: list[Loop] = [], footswitch: list[Loop] = [], midi_program: int=0) -> str:
        context = {
            "bank": active_bank,
            "patch": active_patch,
            "midi_program": midi_program,
        }

        # add loops dynamically
        for i, loop in enumerate(loops, start=1):
            # context[f"loop{i}_status"] = loop.get_css_class()
            context[f"loop{i}_name"] = loop.name

        for i, switch in enumerate(footswitch, start=1):
            # context[f"switch{i}_status"] = switch.get_css_class()
            context[f"switch{i}_name"] = switch.name

        html = self.render_template(self.html, context)

        # return the webpage as a string so we can serve it in our main section
        return html
    
    def render_template(self, template: str, context: dict) -> str:
        for key, val in context.items():
            template = template.replace(f"{{{{ {key} }}}}", str(val))
        return template