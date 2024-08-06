import time
import paramiko
import paramiko.util
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
import os 

# Env
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
devices_ip = ["172.31.105."+str(i) for i in range(1,6)]


## Set up  paramiko SSHClient
client = paramiko.SSHClient()
client.load_system_host_keys()
pvKey = paramiko.RSAKey.from_private_key_file("/home/devasc/.ssh/adminR2_id_rsa")
client.set_missing_host_key_policy( policy= paramiko.AutoAddPolicy())
paramiko.util.log_to_file("paramiko.log")

ip = devices_ip[3]
client.connect(hostname=ip,username=username,disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']},pkey=pvKey)

allResult = []

# Setup Command
def set_ip_vrf(intf,vrf,ip,subnet):
    return [
        f"interface {intf}",
        f"vrf forward {vrf}",
        f"ip address {ip} {subnet}",
        "no shut",
        "exit"
    ]
commands = ["conf t"]
commands += set_ip_vrf("g0/1","control-data","192.168.2.2","255.255.255.0")
commands += set_ip_vrf("g0/2","control-data","192.168.3.1","255.255.255.0")
commands += set_ip_vrf("g0/3","control-data","dhcp","")
commands += ["exit","sh ip vrf interface control-data"]

with client.invoke_shell() as session:
    print(f"Connecting to {ip} ....")

    result = session.recv(6000).decode("ascii")
    allResult.append(result)
    for command in commands:
        print(f"\033[1;33m {command}\033[1;37m")
        session.send(f"{command}\n")
        time.sleep(1.5)
        if "dhcp" in command:
            time.sleep(19)
        result = session.recv(6000).decode("ascii")
        allResult.append(result)
        print(result)
with open("paramiko_result.txt","w+") as f:
    f.write(
    "\n".join(allResult)
    )