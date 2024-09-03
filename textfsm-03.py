from netmiko import ConnectHandler
import sys,re
#from dotenv import load_dotenv
#load_dotenv()  # take environment variables from .env.

# R2_IP
dev_ip = "172.31.105.4"
username = "admin" #os.environ.get("USERNAME") or "admin"
password = "cisco" #os.environ.get("PASSWORD") or "cisco" 


if len(sys.argv)==3:
    print(f"Do you mean interface \"{sys.argv[1]} {sys.argv[2]}\"")
    exit(-1)
test_is_matched =  re.search("([a-zA-Z]+)((\d/\d)|\d)",sys.argv[1].replace(" ",""),re.IGNORECASE) if len(sys.argv)==2 else None
if test_is_matched:
    match_int,match_num,_ = test_is_matched.groups()
else:
    print("Wrong interface name format!")
    exit(-1)

dev_param = {
    "device_type" : "cisco_ios",
    "ip":dev_ip,
    "username":username,
    "password":password
}

command = "show ip int bri"
#print(match_int,match_num)
found_int = False
with ConnectHandler(**dev_param) as ssh:
    result = ssh.send_command(command,use_textfsm=True)
    #print(result)
    for i in result:
        test_is_matched_int = re.search(f"((^{match_int}[a-zA-Z]*){match_num})",i["interface"],re.IGNORECASE)
        if test_is_matched_int:
            found_int = True
            print("Interface: "+i["interface"])
            print("\tIP address = "+i["ip_address"])
            print("\tStatus = "+i["status"])
if not found_int:
    print("No interface found")
        
