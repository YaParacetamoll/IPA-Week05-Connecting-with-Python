import getpass
import telnetlib
import time

# Define the target host and port
HOST = "172.31.105.3"
PORT = 23  # Telnet default port

# Get username and password from user
user = input("username: ")
password = getpass.getpass()

# Create a Telnet connection
tn = telnetlib.Telnet(HOST, PORT, 5)  # 5 is the timeout in seconds

# Read until "Username:" prompt and send username
tn.read_until(b"Username:")
tn.write(user.encode("ascii") + b"\n")
time.sleep(1)  # Wait for a response

# If password is provided, send it after "Password:" prompt
if password:
    tn.read_until(b"Password:")
    tn.write(password.encode("ascii") + b"\n")
    time.sleep(1)

# Configure interface G0/1 with VRF control-data
tn.write(b"configure terminal\n")
time.sleep(2)
tn.write(b"int g0/1\n")
time.sleep(2)
tn.write(b"vrf forwarding control-data\n")
time.sleep(2)
tn.write(b"ip add 192.168.1.1 255.255.255.0\n")
time.sleep(2)
tn.write(b"no shut\n")
time.sleep(2)
tn.write(b"exit\n")
time.sleep(2)

# Configure interface G0/2 with VRF control-data
tn.write(b"int g0/2\n")
time.sleep(2)
tn.write(b"vrf forwarding control-data\n")
time.sleep(2)
tn.write(b"ip add 192.168.2.1 255.255.255.0\n")
time.sleep(2)
tn.write(b"no shut\n")
time.sleep(2)

# Exit configuration mode
tn.write(b"end\n")
time.sleep(2)

# Show interface configuration and verify IP addresses
tn.write(b"show ip vrf interfaces control-data\n")
time.sleep(2)

# Read output and parse it
output = tn.read_very_eager()
output = output.decode("ascii")
output = output.split()

# Expected IP addresses for interfaces
expected_ip = {"Gi0/1": "192.168.1.1", "Gi0/2": "192.168.2.1"}

# Verify IP addresses
for intf in expected_ip.keys():
    try:
        found_intf = output.index(intf)
        found_ip = output[found_intf + 1]
        if found_ip == expected_ip[intf]:
            print(f"{found_ip} of {intf} is assigned to VRF control-data")
        else:
            print("Wrong IP.")
    except Exception as e:
        print(e)

# Close the Telnet connection
tn.close()