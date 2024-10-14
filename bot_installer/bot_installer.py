import paramiko.ssh_exception
import paramiko.util
import paramiko
import threading
import time
import sys

if sys.platform == "win32":
    paramiko.util.log_to_file("nul")
elif sys.platform in ["linux", "linux2"]:
    paramiko.util.log_to_file("/dev/null")

with open("bot_servers.txt", "r") as file:
    hostnames = [x for x in file.read().splitlines() if x.strip() and not x.strip().startswith("#")]
    file.close()

with open("bot_password.txt", "r") as file:
    password = file.read()
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
            
            if not "useragents.txt" in server_files:
                sftp_client.put("dependencies/useragents.txt", "useragents.txt")

            if not "netro_bot.py" in server_files:
                sftp_client.put("dependencies/netro_bot.py", "netro_bot.py")
            
            print(f"Dependencies uploaded to {hostname}. Initializing bot...")

            ssh_client.exec_command("screen -d -m python3 netro_bot.py")
            ssh_client.close()

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
