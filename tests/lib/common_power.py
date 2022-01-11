#--- The Common module is used for Power over the Net - Aten ---

#History
#2020/3/24 first release

import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *

#-----General Setting-----
host = '10.0.0.250'
username = 'administrator'
password = 'password'

#DUT Waiting time
waiting_time=120

#-------------------------

class power_aten:

    def __init_(self,log_power):
        #Need to Init the variable
        #The variable can be used to the other process 

        self.log_power = 'None'
    
    def send_command(self,port,input):
        #Send to all port to power off / on
        #port:ctrl port 1-8
        #input singal: off=0 , on=1

        global log_power
        
        lan.sendline("2\r")    
        lan.expect(prompt)
        time.sleep(1)
        
        lan.sendline("1\r")    
        lan.expect(prompt)
        time.sleep(1)
        
        lan.sendline("2\r")    
        lan.expect(prompt)
        time.sleep(1)
        
        lan.sendline("%s\r" %port)    
        lan.expect(prompt)
        time.sleep(1)
        
        lan.sendline("%s\r" %input)    
        lan.expect(prompt)
        time.sleep(1)
                
        #Exit for Power Over The NET
        for i in range(4):
            lan.sendline("x\r")    
            lan.expect(prompt)
            time.sleep(1)
        time.sleep(5)
        print(colored("\nCtrl_port=%s , input=%s" %(port,input),"yellow"))
        lan.sendline("\n\n\n")    
        lan.expect(prompt)
        lan.sendline("clear")    
        lan.expect(prompt)

        #self.log_power ='Passed - Power Reboot'

        #print(colored("\nNow Waiting for DUT is rebooting , please wait for %s sec" %waiting_time,"yellow"))
        #time.sleep(waiting_time)
        #lan.sendline("clear")
        #lan.expect(prompt)

    def Connect_power_switch(self,port,input):
        global log_power
        n = 0
        time.sleep(5)

        while True:
            lan.sendline("telnet %s" %host)
            try:
                i = lan.expect(["Login:"],timeout=20)
                if i == 0:
                    lan.sendline("%s\r" %username)
                    lan.expect("Password:",timeout=20)
                    lan.sendline("%s\r" %password)
                    lan.expect(prompt)
                    time.sleep(1)
                    print(colored("\nConnected via Power Over the Net","yellow"))                
                    self.send_command(port,input)
                    self.log_power ='Passed'
                    break
                else:
                    self.log_power ='Failed'
            except:
                n += 1
                if n > 5:
                    print(colored("\nUnable to Telnet to Power Over The Net , Will Retry","red"))
                    self.log_telnet = "Failed"
                    msg = "Unable to Telnet to Power Over The Net"
                    self.result_message = msg
                    raise Exception (msg)
                    break


        
