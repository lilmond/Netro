import paramiko.ssh_exception
import paramiko.util
import paramiko
import threading
import time
import sys
import os

CNC_HOSTNAME = "127.0.0.1"
CNC_PASSWORD = "my cool ssh password xd"

if sys.platform == "win32":
    paramiko.util.log_to_file("nul")
elif sys.platform in ["linux", "linux2"]:
    paramiko.util.log_to_file("/dev/null")

def cnc_update():
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=CNC_HOSTNAME, username="root", password=CNC_PASSWORD, timeout=10)

        sftp_client = ssh_client.open_sftp()

        sftp_client.put("netro_cnc.py", "netro_cnc.py")
        sftp_client.put("netro_bot.py", "netro_bot.py")
        sftp_client.put("cnc_help.txt", "cnc_help.txt")

        ssh_client.close()

    except paramiko.ssh_exception.AuthenticationException:
        print(f"Wrong password at {CNC_HOSTNAME}.")
        return
    
    except paramiko.ssh_exception.SSHException:
        print(f"SSH protocol error has occured at {CNC_HOSTNAME}.")
        return
    
def main():
    print("Updating NetroCNC...")
    cnc_update()
    print(f"NetroCNC has successfully been updated.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
