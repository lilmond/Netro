# Netro
A centralized Python botnet that currently supports HTTP, TCP and UDP flood attacks.

## Table Of Contents
- [Requirements](https://github.com/lilmond/Netro?tab=readme-ov-file#requirements)
- [Latest Updates](https://github.com/lilmond/Netro/edit/main/README.md#latest-updates)
- [CNC Installation](https://github.com/lilmond/Netro/edit/main/README.md#cnc-installation)
  - [Windows 10 Source Code Download](https://github.com/lilmond/Netro/edit/main/README.md#for-linux-users)
  - [Linux Source Code Installation](https://github.com/lilmond/Netro/edit/main/README.md#latest-updates)
  - [Setting Up Configuration](https://github.com/lilmond/Netro/edit/main/README.md#setting-configuration)
  - [Preparing The CNC](https://github.com/lilmond/Netro/edit/main/README.md#preparing-cnc)
- [Bot Installation](https://github.com/lilmond/Netro/edit/main/README.md#bot-installation)

![image](https://github.com/user-attachments/assets/0995d4df-27ab-428d-b548-a3f17e903ae4)


# Requirements
- 1 VPS for CNC (please prefer a high-end)
- 1 or as many as you want **Ubuntu 24.04** VPS to deploy some bots.
- Basic understanding in coding.

# Latest Updates
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

## Manual Installation

Log into your bot VPS and install the required componants by executing the following commands:
```bash
sudo apt install git -y
sudo apt install python3.12-venv -y
sudo apt install python3-pip -y
sudo apt install tor -y
```

You may then upload **netro_bot.py**, **cnc_config.json** and **bot_manual_requirements.txt** into the bot server. Either with **scp** or **MobaXterm**'s server file manager.

And finally, run the commands below to deploy the bot.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
screen -d -m python3 netro_bot.py
```

Check it is running using
```
screen -ls
```

"There is a screen on:" indicates that it is running.

![image](https://github.com/user-attachments/assets/3d676192-aa7e-4f42-8a7f-f39fe3250399)

"No Sockets found in..." indicates that there was an error running the script.

![image](https://github.com/user-attachments/assets/bdbd9535-a7f7-459d-8868-f92f9bb518a3)

If you come across with this issue. You may submit an issue on my GitHub repository page at https://github.com/lilmond/Netro/issues and I can help. Please don't forget to submit an error log by running the script normally using the follow command:

```bash
python netro_bot.py
```

You may however do a bit of experiment and try to fix it yourself.

And finally, you may go back to your CNC server and check if your bots have successfully connected. I will show an example below.

![image](https://github.com/user-attachments/assets/6d70d786-ca71-43fc-b480-42576fdb9da9)

Note that it's 0 in the example shown above because I am not running any bots right now.

But if it says 0 to you, then your bots are probably not running. Or there was a mistake in the bot's server **cnc_config.json**


# Etc
Discord: https://discord.com/invite/Bnf3e8pkyj
Buy me a coffee: 17nXfqRRiSGDpx1XEh3veHA6gyCLAktFk9
