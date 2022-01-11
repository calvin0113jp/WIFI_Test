#--- The Common module is used for tftp command ----



import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *


class scp_command:

    def SCP_Send_file_To_Remote(self,ip,account,pw,local_file,remote_file):
        # ssh scp config

        try:
            lan.sendline("scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '%s' %s@%s:/home && echo 'scp pass' || echo 'fail'" %(local_file,account,ip,remote_file))
            i = lan.expect(["assword:", "Last login"], timeout=30)
            if i == 0:
                lan.sendline(pw)
                time.sleep(2)
                i = lan.expect(["pass", "fail"], timeout=30)
                if i == 0:
                    print(colored("\nSCP Send Pass","yellow"))
                    lan.expect(prompt)
                    return True
                elif i == 1:
                    print(colored("\nSCP Send Fail","red"))
                    lan.expect(prompt)
                    return False     
        except:
            print(colored("\nSCP command fail","red"))
            return False
    
    def device_logout(self):
        # Exit the SecurityHole 

        try:
            lan.sendline("quit")
            lan.expect(prompt,timeout=10)
            print(colored("\nExit the Device","yellow"))
        except:
            print(colored("\nUnable to Exit the Device","red")) 

    # def start_tcpdump(self,interface,filter,output_file):
    #     # Capture the packet
    #     # interface : eth1 or eth2
    #     # filter : input data filter
    #     # output_file : file name

    #     print(colored("\nStatrting to capture packet","yellow"))
    #     lan.sendline("\ntcpdump -i %s -A %s -q -l > %s &" %(interface,filter,output_file))
    #     lan.expect(prompt)
    #     lan.sendline("\n\n\n")
    #     lan.expect(prompt)

    # def kill_tcpdump(self):
    #     #Kill the tcpdump process

    #     print(colored("\nKill process of tcpdump","yellow"))
    #     lan.sendline("killall tcpdump")
    #     lan.expect(prompt)
    #     lan.sendline("\n\n\n")
    #     lan.expect(prompt)   
