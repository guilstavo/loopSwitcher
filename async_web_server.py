import uasyncio as asyncio
import network
import json
from typing import Optional
from patch import Patch
from bank_manager import BankManager
from file import Html, Json

class AsyncWebServer:
    def __init__(self, config_file="network_config.json"):
        # Network
        config = Json(config_file).data
        self.access_point = config.get("access_point", False)
        self.webPage = WebPage()
        self.bankManager = BankManager()
        self.current_patch: Optional[Patch] = self.bankManager.get_active_patch()

        # State
        self.loops = self.current_patch.looper.get_loops() if self.current_patch else []
        self.footswitch = self.current_patch.looper.get_footswitch() if self.current_patch else []
        self.midi_program = self.current_patch.midiPresets[0].program if self.current_patch else 0
        self.sse_clients = set()

        # Connect Wi-Fi
        if self.access_point:
            self.ap = self.access_point_setup(config)
            self.ip = self.ap.ifconfig()[0]
        else:
            self.wlan = self.connect(config)
            self.ip = self.wlan.ifconfig()[0]

        print("Network ready, IP:", self.ip)

    # ---------- Network ----------
    def connect(self, cfg):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        ssid = cfg.get("ssid")
        pw = cfg.get("password")
        ip = cfg.get("ip")
        subnet = cfg.get("subnet")
        gw = cfg.get("gateway")
        dns = cfg.get("dns")
        if ip:
            wlan.ifconfig((ip, subnet, gw, dns))
        wlan.connect(ssid, pw)
        while not wlan.isconnected():
            print("Connecting to Wi-Fi...")
        print("Connected:", wlan.ifconfig())
        return wlan

    def access_point_setup(self, cfg):
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=cfg.get("ap_ssid", "PicoServer"),
                  password=cfg.get("ap_password", "12345678"))
        while not ap.active():
            print("Starting AP...")
        print("AP ready:", ap.ifconfig())
        return ap

    # ---------- SSE broadcast ----------
    async def broadcast(self):
        while True:
            if not self.sse_clients:
                await asyncio.sleep(0.5)
                continue

            data = {
                "bank": self.bankManager.get_active_bank_name(),
                "patch": self.bankManager.get_active_patch_name(),
                "midi_program": self.midi_program,
                "classes": {}
            }
            for i, loop in enumerate(self.loops, start=1):
                data["classes"][f"loop{i}_status"] = loop.get_css_class()
            for i, sw in enumerate(self.footswitch, start=1):
                data["classes"][f"switch{i}_status"] = sw.get_css_class()

            msg = f"data: {json.dumps(data)}\n\n"

            dead_clients = set()
            for client in self.sse_clients:
                try:
                    await client.awrite(msg)
                    await client.drain()
                except Exception:
                    dead_clients.add(client)

            self.sse_clients -= dead_clients
            await asyncio.sleep(1)

    # ---------- Handle each client ----------
    async def serve_client(self, reader, writer):
        try:
            # Read request line
            request_line = await reader.readline()
            if not request_line:
                await writer.aclose()
                return
            method, path, *_ = request_line.decode().split()

            # Read headers
            headers = {}
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b""):
                    break
                parts = line.decode().split(":", 1)
                if len(parts) == 2:
                    headers[parts[0].lower()] = parts[1].strip()

            # --- SSE ---
            if method.upper() == "GET" and path == "/events":
                await writer.awrite(
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/event-stream\r\n"
                    "Cache-Control: no-cache\r\n"
                    "Connection: keep-alive\r\n\r\n"
                )
                self.sse_clients.add(writer)
                return

            # --- POST ---
            if method.upper() == "POST":
                content_length = int(headers.get("content-length", 0))
                body = await reader.read(content_length) if content_length else b""
                request_value = body.decode().strip()
                print("POST received:", repr(request_value))

                # Update patch
                self.current_patch = self.switch(request_value, self.current_patch)

                # Send simple 200 OK to avoid ECONNRESET
                resp = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK"
                await writer.awrite(resp)
                await writer.aclose()
                return

            # --- Serve HTML ---
            html = self.webPage.render(self.bankManager.get_html_context(self.current_patch))

            resp = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(html)}\r\n"
                "Connection: close\r\n\r\n"
                + html
            )
            await writer.awrite(resp)
            await writer.aclose()

        except Exception as e:
            print("serve_client error:", e)
            try:
                await writer.aclose()
            except:
                pass

    # ---------- Switch logic ----------
    def switch(self, request: Optional[str], currentPatch: Optional[Patch]) -> Optional[Patch]:
        if request is None:
            return currentPatch
        if request == "bank=up":
            self.bankManager.move_up_bank()
        elif request == "bank=down":
            self.bankManager.move_down_bank()
        elif request.startswith("patch="):
            idx = int(request.split("=")[1]) - 1
            return self.bankManager.select_patch(idx)
        return currentPatch

    # ---------- Run server ----------
    async def run(self):
        print("Starting server on 0.0.0.0:80")
        server = await asyncio.start_server(self.serve_client, "0.0.0.0", 80)
        asyncio.create_task(self.broadcast())

        # Keep program alive
        while True:
            await asyncio.sleep(3600)

# ---------- Web page rendering ----------
class WebPage:
    def __init__(self):
        self.html = Html("index.html").data

    def render(self, context):
        template = self.html
        for k, v in context.items():
            template = template.replace(f"{{{{ {k} }}}}", str(v))
        return template
