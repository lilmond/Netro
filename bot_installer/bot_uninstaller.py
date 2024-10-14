import paramiko.ssh_exception
import paramiko.util
import paramiko
import threading
import time
import sys
import os

BOT_SERVERS_PATH = "bot_servers.txt"
BOT_PASSWORD_PATH = "bot_password.txt"

for file in [BOT_SERVERS_PATH, BOT_PASSWORD_PATH]:
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

def server_install(hostname: str):
    tries = 0

    while True:
        try:
            tries += 1

            if tries > 3:
                print(f"Max uninstallation retries at {hostname}. Quiting...")
                break

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname, username="root", password=password, timeout=10)
            stdin, stdout, stderr = ssh_client.exec_command("pkill screen")
            print(stdout.read())
            stdin, stdout, stderr = ssh_client.exec_command("rm -rf netro_bot.py useragents.txt")
            print(stdout.read())

            ssh_client.close()

            print(f"Uninstalled NetroBot at {hostname}")

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
    
    print(f"NetroBot uninstallation completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
