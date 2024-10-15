import paramiko.ssh_exception
import paramiko.util
import paramiko
import threading
import time
import sys
import os

BOT_SERVERS_PATH = "bot_servers.txt"
BOT_PASSWORD_PATH = "bot_password.txt"

NETRO_BOT_PATH = "../netro_bot.py"
USERAGENTS_PATH = "../useragents.txt"
BOT_PACKAGES_PATH = "../bot_packages.txt"
BOT_REQUIREMENTS_PATH ="../bot_requirements.txt"

for file in [BOT_SERVERS_PATH, BOT_PASSWORD_PATH, NETRO_BOT_PATH, USERAGENTS_PATH, BOT_PACKAGES_PATH, BOT_REQUIREMENTS_PATH]:
    if not os.path.exists(file):
        print(f"Required file not found: {file}")
        exit()

if sys.platform == "win32":
    paramiko.util.log_to_file("nul")
elif sys.platform in ["linux", "linux2"]:
    paramiko.util.log_to_file("/dev/null")

with open(BOT_SERVERS_PATH, "r") as file:
    hostnames = [x for x in file.read().splitlines() if x.strip() and not x.strip().startswith("#")]
    file.close()

with open(BOT_PASSWORD_PATH, "r") as file:
    password = file.read()
    file.close()

with open(BOT_PACKAGES_PATH, "r") as file:
    bot_packages = [x for x in file.read().splitlines() if x.strip()]
    file.close()
    
with open(BOT_REQUIREMENTS_PATH, "r") as file:
    bot_requirements = [x for x in file.read().splitlines() if x.strip()]
    file.close()

def server_install(hostname: str):
    tries = 0

    while True:
        try:
            tries += 1

            if tries > 3:
                print(f"Max installation retries at {hostname}. Quiting...")
                break

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname, username="root", password=password, timeout=10)
            stdin, stdout, stderr = ssh_client.exec_command("ls")
            
            server_files = stdout.read().decode().splitlines()
            
            if all(["useragents.txt" in server_files, "netro_bot.py" in server_files]):
                print(f"NetroBot is already installed at {hostname}.")
                ssh_client.close()
                return
            
            print(f"Installing NetroBot at {hostname}...")
            
            sftp_client = ssh_client.open_sftp()
            
            if not "netro_bot.py" in server_files:
                sftp_client.put(NETRO_BOT_PATH, "netro_bot.py")

            if not "useragents.txt" in server_files:
                sftp_client.put(USERAGENTS_PATH, "useragents.txt")
            
            print(f"Dependencies uploaded to {hostname}. Installing required packages...")
            
            for package in bot_packages:
                stdin, stdout, stderr = ssh_client.exec_command(f"apt install {package} -y")
                stdout.read()

            for package in bot_requirements:
                stdin, stdout, stderr = ssh_client.exec_command(f"apt install python3-{package} -y")
                stdout.read()
            
            print(f"Required packages installed. Initializing NetroBot at {hostname}...")

            stdin, stdout, stderr = ssh_client.exec_command("service tor start")
            stdout.read()

            stdin, stdout, stderr = ssh_client.exec_command("screen -d -m python3 netro_bot.py")
            stdout.read()

            ssh_client.close()

            break

        except paramiko.ssh_exception.AuthenticationException:
            print(f"Wrong password at {hostname}.")
            return
        
        except paramiko.ssh_exception.SSHException:
            print(f"SSH protocol error has occured at {hostname}. Retrying...")
            continue
    
def main():
    max_threads = 10

    for hostname in hostnames:
        while True:
            if threading.active_count() >= max_threads:
                time.sleep(0.05)
                continue

            threading.Thread(target=server_install, args=[hostname], daemon=True).start()
            break

    while True:
        time.sleep(0.05)

        if threading.active_count() <= 1:
            break
    
    print(f"NetroBot installation completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
