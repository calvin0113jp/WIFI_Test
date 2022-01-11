#--- The Common module is used for Tcpdump command ----
#--- For security hole server ---

import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *


class tcpdump_command:

    def connect_to_device(self,ip='10.0.0.10',user='root',pw='123456',port='22'):
        # Connect to security hole

        n = 0
        while True:
            try:
                lan.sendline("ssh %s@%s -p %s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" % (user, ip, port))
                i = lan.expect(["yes/no", "assword:", "Last login"], timeout=30)
                if i == 0:
                    lan.sendline("yes")
                    i = self.expect(["Last login", "assword:"])
                    print(colored("\nConnected to SecurityHole","yellow"))
                    break
                if i == 1:
                    lan.sendline(pw)
                    lan.expect(prompt)
                    print(colored("\nConnected to SecurityHole","yellow"))
                    break
            except:
                n += 1
                if n > 10:
                    print(colored("\nUnable to Connect to SecurityHole","red"))
                    msg = "Unable to Connect to SecurityHole"
                    self.result_message = msg
                    raise Exception(msg)
                    break
    
    def device_logout(self):
        # Exit the SecurityHole 

        try:
            lan.sendline("exit")
            lan.expect("logout",timeout=10)
            lan.expect(prompt,timeout=10)
            print(colored("\nExit the SecurityHole","yellow"))
        except:
            print(colored("\nUnable to Exit the SecurityHole","red")) 

    def start_tcpdump(self,interface,filter,output_file):
        # Capture the packet
        # interface : eth1 or eth2
        # filter : input data filter
        # output_file : file name

        print(colored("\nStatrting to capture packet","yellow"))
        lan.sendline("\ntcpdump -i %s -A %s -q -l > %s &" %(interface,filter,output_file))
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)

    def kill_tcpdump(self):
        #Kill the tcpdump process

        print(colored("\nKill process of tcpdump","yellow"))
        lan.sendline("killall tcpdump")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)   
