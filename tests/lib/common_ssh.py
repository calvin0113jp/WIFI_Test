#--- The Common module is used for ssh command ----


import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *
from common_ping import *

class ssh_command:

    def connect_to_device(self,ip,user,pw,port='22'):
        # Connect to DUT

        n = 0
        while True:
            try:
                msg = "Connected to DUT via SSH"

                lan.sendline("ssh %s@%s -p %s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" % (user, ip, port))
                i = lan.expect(["yes/no", "assword:", "Last login"], timeout=30)
                if i == 0:
                    lan.sendline("yes")
                    i = self.expect(["Last login", "assword:"])
                    print(colored("\nConnected to DUT via SSH","yellow"))                    
                    return msg
                    break
                if i == 1:
                    lan.sendline(pw)
                    lan.expect(prompt)
                    print(colored("\nConnected to DUT via SSH","yellow"))
                    return msg
                    break
            except:
                n += 1
                if n > 5:
                    print(colored("\nUnable to Connect to DUT via SSH","red"))
                    msg = "Unable to Connect to DUT via SSH"
                    return msg
                    break

    def device_logout(self):
        # Exit the DUT 

        try:
            lan.sendline("exit")
            lan.expect("closed",timeout=10)
            lan.expect(prompt,timeout=10)
            print(colored("\nExit the DUT","yellow"))
        except:
            print(colored("\nUnable to Exit the DUT","red")) 

    def main(self,ip,user,pw):
        # Main process
        # Ping to DUT if alive
        # ssh to device

        ping_check = Ping()
        ping_result = ping_check.waiting_dut_bootup(ip)
        
        if 'Pass' in ping_result:
            msg = self.connect_to_device(ip,user,pw)
        else:
            msg = 'Unable to ping to DUT over 10 times'

        return msg

    def get_cli_regular_result(self,cli,regux,expect_value):
        # Regular the value

        lan.sendline("\n%s" %cli)
        lan.expect(regux)
        regux_result = lan.match.group(1)
        print (regux_result)

        if expect_value in regux_result:
            print(colored("\nCli Result Matched!","yellow"))
            return True
        else:
            print(colored("\nCLi Result Does Not Matched!","red"))
            return False
            
    

