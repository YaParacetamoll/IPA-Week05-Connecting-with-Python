from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
import yaml

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

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('/templates/router-nat.j2')
config_commands = template.render(config_data)

device = {
    "device_type": "cisco_ios",
    "host": "172.31.105.4",
    "username": "admin",
    "password": "cisco",
    "secret": "cisco",
}

with open("data/routers-nat.yml") as f:
    routers = yaml.safe_load(f)

for router in routers:
    router_conf = "config/" + router["name"] + "-nat.txt"
    with open(router_conf, "w") as f:
        f.write(template.render(router))

with ConnectHandler(**device) as net_connect:

    net_connect.enable()
    net_connect.send_config_set(config_commands.splitlines())
    print("Configuration applied successfully.")


    ping_results = []
    for interface in ["g0/1", "g0/2"]:
        result = net_connect.send_command(f"ping vrf control-data 8.8.8.8 source {interface}")
        ping_results.append(result)

    print("\n".join(ping_results))