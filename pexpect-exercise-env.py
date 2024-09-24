import pexpect
import time
import os


# กำหนด username และ password 
username = os.environ.get("TELNET_USERNAME")
password = os.environ.get("TELNET_PASSWORD")


r1_ip = '172.31.105.3'
r2_ip = '172.31.105.4'



loopback_ip_r1 = '172.16.1.1'
loopback_ip_r2 = '172.16.2.2'

def configure_router(ip, loopback_ip):
    try:
        # Start the telnet session
        session = pexpect.spawn(f'telnet {ip}', timeout=30)
        
        # Log the session for debugging
        session.logfile = open(f'{ip}_session.log', 'wb')
        
        session.expect('Username:')
        session.sendline(username)
        session.expect('Password:')
        session.sendline(password)
        
        #Enter configuration mode
        session.expect('#')
        session.sendline('configure terminal')
        session.expect('#')
        
        # Configure loopback interface
        session.sendline('interface loopback 0')
        session.expect('#')
        session.sendline(f'ip address {loopback_ip} 255.255.255.255')
        session.expect('#')
        session.sendline('exit')
        
        # Verify the configuration
        session.sendline('do show ip interface brief')
        time.sleep(5)
        session.expect('#')

        # Exit configuration mode
        session.sendline('end')
        session.expect('#')
        
        output = session.before.decode('utf-8')
        print(f'Output from {ip}:\n{output}')

        if loopback_ip in output:
            print(f'Loopback 0 on {loopback_ip} is created on {ip}')
        else:
            print(f'Failed to create Loopback 0 on {ip}')
        
        # Close the session
        session.sendline('exit')
        session.expect(pexpect.EOF)
        session.close()
        
    except pexpect.exceptions.TIMEOUT:
        print(f'Timeout error while connecting to {ip}')
    except Exception as e:
        print(f'Error: {e}')

# Configure R1-P
configure_router(r1_ip, loopback_ip_r1)

# Configure R2-P
configure_router(r2_ip, loopback_ip_r2)

