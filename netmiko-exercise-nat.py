from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import os
import yaml

load_dotenv(dotenv_path='.env.example')

config_data = {
    "acl_list": [
        {"number": 1, "network": "192.168.1.0", "wildcard": "0.0.0.255"},
        {"number": 1, "network": "192.168.2.0", "wildcard": "0.0.0.255"},
        {"number": 1, "network": "192.168.3.0", "wildcard": "0.0.0.255"},
    ],
    "nat_acl": 1,
    "nat_interface": "GigabitEthernet0/3",
    "vrf_name": "control-data",
    "inside_interfaces": "g0/1, g0/2",
    "outside_interface": "g0/3"
}

# โหลด template Jinja2 จากโฟลเดอร์ templates
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('templates/router-nat.j2')

with open("data/routers-nat.yml") as f:
    routers = yaml.safe_load(f)

for router in routers:
    router_conf = "config/" + router["name"] + "-nat.txt"
    with open(router_conf, "w") as f:
        f.write(template.render(router))

# เรนเดอร์คอนฟิกจาก template และ config_data
config_commands = template.render(config_data).splitlines()

# ข้อมูลการเชื่อมต่อไปยัง Router
device = {
    "device_type": "cisco_ios",
    "host": "172.31.105.4",
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
    "secret": os.getenv("PASSWORD"),
}

device2 = {
    "device_type": "cisco_ios",
    "host": "172.31.105.3",
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
    "secret": os.getenv("PASSWORD"),
}

# เชื่อมต่อไปยัง Router ด้วย Netmiko
with ConnectHandler(**device) as net_connect:
    net_connect.enable()  # เข้าสู่โหมด enable

    # ส่งคำสั่งคอนฟิกไปยัง Router
    output = net_connect.send_config_set(config_commands)
    print("Configuration applied successfully:")
    print(output)

    # ทดสอบการ ping จากอินเตอร์เฟซใน vrf control-data
    ping_results = []
    for interface in ["g0/1", "g0/2"]:
        result = net_connect.send_command(f"ping vrf control-data 8.8.8.8 source {interface}")
        ping_results.append(result)
    
    print("\n*****************************************************")
    print(f"Ping result from {device['host']}:")
    print("\n".join(ping_results))

    net_connect.disconnect()

with ConnectHandler(**device2) as net_connect:
    ping_results = []
    for interface in ["g0/1", "g0/2"]:
        result = net_connect.send_command(f"ping vrf control-data 8.8.8.8 source {interface}")
        ping_results.append(result)
    print("\n****************************************************")
    print(f"Ping result from {device2['host']}:")
    print("\n".join(ping_results))
    
    net_connect.disconnect()
