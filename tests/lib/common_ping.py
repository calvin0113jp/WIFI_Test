#---The Common module is used for Ping---

#History
#2020/3/24 First release

import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *


class Ping:
    
    def waiting_dut_bootup(self,dut_ip):
        #Waiting dut bootup

        n = 0
        while True:
            try:
                print(colored("\nChecking for DUT status , Waiting...","yellow"))
                lan.sendline("ping -c5 -W 1 %s " % (dut_ip))
                lan.expect("5 (packets )?received", timeout=30)
                lan.expect(prompt)
                ping_result = 'Pass'
                print(colored("\nDUT is bootup ok...","yellow"))
                return ping_result
                break
            except:
                print(colored("\nDUT is down , Waiting for DUT is up...","red"))
                n += 1
                if n > 10:
                    msg = 'Unable to ping to DUT over 10 times'
                    ping_result = 'Fail'
                    return ping_result
                    break

    def ping_client(self,interface,client):
        # Ping client

        n = 0
        while True:
            try:
                print(colored("\nStarting to ping client , Waiting...","yellow"))
                lan.sendline("ping -I %s -c5 -W 1 %s " % (interface,client))
                lan.expect("5 (packets )?received", timeout=30)
                lan.expect(prompt)
                ping_result = 'Pass'
                print(colored("\nPing to client successfully...","yellow"))
                return ping_result
                break
            except:
                print(colored("\nUnable to ping client , Retry again...","red"))
                n += 1
                if n > 3:
                    msg = 'Unable to ping over 3 times'
                    ping_result = 'Fail'
                    return ping_result
                    break

    def ping_ipaddress(self,interface,ip):
        # Ping ip address

        n = 0
        while True:
            try:
                print(colored("\nStarting to ping ipaddress , Waiting...","yellow"))
                lan.sendline("ping -I %s -c5 -W 1 %s " % (interface,ip))
                lan.expect("5 (packets )?received", timeout=30)
                lan.expect(prompt)
                ping_result = 'Pass'
                print(colored("\nPing to ipaddress successfully...","yellow"))
                return ping_result
                break
            except:
                print(colored("\nUnable to ping ipaddress , Retry again...","red"))
                n += 1
                if n > 3:
                    msg = 'Unable to ping over 3 times'
                    ping_result = 'Fail'
                    return ping_result
                    break