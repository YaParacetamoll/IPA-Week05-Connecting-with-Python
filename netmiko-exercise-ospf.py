from netmiko import ConnectHandler
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env.example')
import os

# กำหนด username และ password
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# รายการ IP ของอุปกรณ์
device_ip = ["172.31.105.3", "172.31.105.4"]

# Loop ผ่านแต่ละ IP address
for dip in device_ip:
    # สร้างตัวแปร dictionary เพื่อเก็บข้อมูลการเชื่อมต่อ
    device_config = {
        "device_type": "cisco_ios",
        "ip": dip,
        "username": username,
        "password": password,
    }

    try:
        # ใช้ ConnectHandler เพื่อเชื่อมต่อกับอุปกรณ์
        with ConnectHandler(**device_config) as ssh:

            # ตรวจสอบ IP และส่งคำสั่งที่แตกต่างกันไปยังอุปกรณ์
            if dip == "172.31.105.3":
                ssh.send_config_set([
                    'router ospf 1 vrf control-data',
                    'network 192.168.1.0 0.0.0.255 area 0',
                    'network 192.168.2.0 0.0.0.255 area 0',
                    'exit',
                    'write memory'
                ])
            if dip == "172.31.105.4":
                ssh.send_config_set([
                    'router ospf 1 vrf control-data',
                    'network 192.168.2.0 0.0.0.255 area 0',
                    'network 192.168.3.0 0.0.0.255 area 0',
                    'default-information originate',
                    'exit',
                    'write memory'
                ])

            # ดึงข้อมูล routing table
            result = ssh.send_command("show ip route vrf control-data")
            

            # ตรวจสอบและพิมพ์ผลลัพธ์
            if dip == "172.31.105.3":
                if "192.168.3.0/24" in result:
                    print("Test routing R1 passes: 192.168.3.0/24 found on R1")
                if "0.0.0.0/0" in result:
                    print("Test routing R1 passes: default route found on R1")
            elif dip == "172.31.105.4":
                if "192.168.1.0/24" in result:
                    print("Test routing R2 passes: 192.168.1.0/24 found on R2")

    except Exception as e:
        print(f"An error occurred with device {dip}: {e}")