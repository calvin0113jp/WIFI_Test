#--- The Common module is used for Internet Switch ---
#--- SOARNEX EP-220-28 Series ---

# History
# 2020/12/14 first release
# Vlan ID 2 - dhcp - Port 1-2 untagged
# Vlan ID 3 - Security ETH2 - Port 1 , 3-4 untagged
# Vlan ID 4 - CDRouter - Port 1 , 5-6 untagged
# Vlan ID 5 - PPPoE - Port 1 , 7-8 untagged
# Vlan ID 6 - Reserved2 - Port 1 , 9-10 untagged
# Others port - keep default

import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *

#-----General Setting-----

host = '10.0.0.240'
username = 'admin'
password = 'admin'

#DUT Waiting time
waiting_time = 10

#-------------------------

class switch_ctrl:
    
    def send_command(self,pvid):
        lan.sendline("configure terminal")
        lan.expect(prompt)
        time.sleep(1)
        lan.sendline("interface gigabitethernet 1")
        lan.expect(prompt)
        time.sleep(1)
        lan.sendline("switchport pvid %s" %pvid)
        lan.expect(prompt)      
        time.sleep(1)
        lan.sendline("end")
        lan.expect(prompt)
        time.sleep(1)
        lan.sendline("logout")
        time.sleep(3)
        lan.expect("Connection closed by foreign host",timeout=20)
        time.sleep(3)
        lan.expect(prompt)

        if pvid == '2':
            switch_type = 'DHCP Port 1-2'
        elif pvid == '3':
            switch_type = 'Security ETH2 port 1,3-4'
        elif pvid == '4':
            switch_type = 'CDRouter port 1,5-6'
        elif pvid == '5':
            switch_type = 'PPPoE 1,7-8'
        elif pvid == '6':
            switch_type = 'Reserved2 port 1,9-10'
        
        print(colored("\nSelect interface to %s , Waiting VLAN Switch for %s sec " %(switch_type,waiting_time) ,"yellow"))
        time.sleep(waiting_time)

    def Connect_switch(self,pvid):
        n = 0
        print(colored("\nSwitching the WAN interface , Please wait...","yellow"))
        time.sleep(5)

        while True:
            lan.sendline("telnet %s" %host)
            try:
                i = lan.expect(["login: "],timeout=20)
                if i == 0:
                    lan.sendline("%s" %username)
                    time.sleep(2)
                    lan.expect("Password: ",timeout=20)
                    lan.sendline("%s" %password)
                    lan.expect(prompt,timeout=20)
                    time.sleep(1)
                    lan.sendline("\n\n\n")
                    lan.expect(prompt)
                    print(colored("\nConnected via VLAN Switch","yellow"))                
                    self.send_command(pvid)
                    log_switch = True
                    break
                else:
                    log_switch = False
            except:
                n += 1
                if n > 5:
                    print(colored("\nUnable to Telnet to Switch, Will Retry","red"))
                    log_telnet = "Failed"
                    msg = "Unable to Telnet to VLAN Switch"
                    log_switch = False
                    self.result_message = msg
                    raise Exception (msg)
                    break
        
        return log_switch


        
