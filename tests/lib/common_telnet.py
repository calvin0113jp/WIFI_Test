#---The Common module is used for Telnet---

#History
#2020/1/7 First release
#2020/2/11 Connect_telnet - add retry 

#import re
#import os
#import sys
#import rootfs_boot
#import subprocess
import time
#import json
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *

#-----General Setting-----
#local setting
tftp_server_apresia = '10.0.0.100'
tftp_server_trendnet = '192.168.10.100'
tftp_server_dgsme = '10.90.90.100'

#DUT Waiting time
waiting_time=120

#-------------------------

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
                print(colored("\nDUT is bootup ok...","yellow"))
                break
            except:
                print(colored("\nDUT is down , Waiting for DUT is up...","red"))
                n += 1
                if n > 30:
                    msg = 'Unable to connect to DUT over 20 times'
                    self.result_message = msg
                    raise Exception (msg)
                    break

class Telnet:
    
    def __init_(self,log_telnet):
        #Need to Init the variable
        #The variable can be used to the other process 

        self.log_telnet = 'None'
    
    def Connect_telnet(self,host,username,password):
        
        global log_telnet
        n = 0
        while True:
            try:
                lan.sendline("telnet %s" %host)
                i = lan.expect(["login: ","UserName: ","Username: "],timeout=20)            
                if i == 0:
                    lan.sendline("%s" %username)
                    time.sleep(2)
                    lan.expect("Password: ",timeout=20)
                    lan.sendline("%s" %password)
                    lan.sendline("\n\n\n")
                    lan.expect(prompt)
                    print(colored("\nConnected via Telnet","yellow"))                
                    self.log_telnet ='Passed'
                    break
            
                elif i == 1:
                    lan.sendline("%s" %username)
                    time.sleep(2)
                    lan.expect("Password: ")
                    lan.sendline("%s" %password)
                    lan.expect(prompt)
                    lan.sendline("\n\n\n")
                    lan.expect(prompt)
                    print(colored("\nConnected via Telnet","yellow"))                
                    self.log_telnet ='Passed'
                    break

                elif i == 2:
                    lan.sendline("%s" %username)
                    time.sleep(2)
                    lan.expect("Password: ")
                    lan.sendline("%s" %password)
                    lan.expect(prompt)
                    lan.sendline("\n\n\n")
                    lan.expect(prompt)
                    print(colored("\nConnected via Telnet","yellow"))                
                    self.log_telnet ='Passed'
                    break
                
            except:
                n += 1
                if n > 5:
                    print(colored("\nUnable to Telnet to DUT , Will Retry","red"))
                    self.log_telnet = "Failed"
                    msg = "Unable to Telnet to DUT"
                    self.result_message = msg
                    raise Exception (msg)
                    break

    def Disconnect_telnet(self):
        global log_telnet
        
        try: 
            lan.sendline("exit")
            time.sleep(3)
            lan.expect("Connection closed by foreign host",timeout=20)
            time.sleep(3)
            lan.expect(prompt)
            
            print(colored("\nDisconnected Telnet","yellow"))
            self.log_telnet = 'exit telnet'
        except:
            print(colored("\nUnable to Disconnected Telnet","yellow"))
            self.log_telnet = 'Unable to exit telnet'
    
    def SaveConfig(self,model,id):
        #Save Config to local via tftp server
        #model= model list
        #id =config id

        if "Apresia" in model:
            try:
                lan.sendline("upload cfg_toTFTP %s config_id %s" %(tftp_server_apresia,id))
                lan.expect("successfully")
                lan.expect(prompt)
                lan.sendline("logout")
                lan.expect(prompt)
                self.log_telnet = "Upload config - Passed"
            except:
                self.log_telnet = "Upload config - Failed"
        
        elif "Trendnet" in model:
            try:
                lan.sendline("upload cfg_toTFTP %s config_id %s" %(tftp_server_trendnet,id))
                lan.expect("successfully")
                lan.expect(prompt)
                lan.sendline("logout")
                lan.expect(prompt)
                self.log_telnet = "Upload config - Passed"
            except:
                self.log_telnet = "Upload config - Failed"
        
        elif "ME" in model:
            try:
                lan.sendline("upload cfg_toTFTP %s config_id" %(tftp_server_dgsme))
                lan.expect("success",timeout=30)
                lan.expect(prompt)
                lan.sendline("logout")
                lan.expect(prompt)
                self.log_telnet = "Upload config - Passed"
            except:
                self.log_telnet = "Upload config - Failed"
    
        elif "DXS" in model:
            try:
                lan.sendline("copy startup-config tftp://%s/config_id" %(tftp_server_dgsme))
                lan.expect("successful",timeout=30)
                lan.expect(prompt)
                lan.sendline("logout")
                lan.expect(prompt)
                self.log_telnet = "Upload config - Passed"
            except:
                self.log_telnet = "Upload config - Failed"

    def LoadConfig(self,model,id):
        #load Config to local via tftp server
        #model = model list
        #id = config id 1 or 2
        
        if "Apresia" in model:
            try:
                lan.sendline("download cfg_fromTFTP %s config_id %s" %(tftp_server_apresia,id))
                lan.expect("successfully")
                lan.expect("Connection closed",timeout=20)
                lan.expect(prompt)
                self.log_telnet = "Download config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time) 
            except:
                self.log_telnet = "Download config - Failed"
        
        elif "Trendnet" in model:
            try:
                lan.sendline("download cfg_fromTFTP %s config_id %s" %(tftp_server_trendnet,id))
                lan.expect("successfully")
                lan.expect("Connection closed",timeout=20)
                lan.expect(prompt)
                self.log_telnet = "Download config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time) 
            except:
                self.log_telnet = "Download config - Failed"
        
        elif "ME" in model:
            try:
                lan.sendline("download cfg_fromTFTP %s config_id config_id %s" %(tftp_server_dgsme,id))
                lan.expect("successful",timeout=30)
                lan.expect(prompt)
                lan.sendline("reboot force_agree")
                lan.expect(prompt)
                self.log_telnet = "Download config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time)            
            except:
                self.log_telnet = "Download config - Failed"
        
        elif "DXS" in model:
            try:
                lan.sendline("copy tftp://%s/config_id startup-config" %(tftp_server_dgsme))
                lan.expect("successful",timeout=30)
                lan.expect(prompt)
                lan.sendline("reboot force_agree")
                lan.expect(prompt)
                self.log_telnet = "Download config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time)            
            except:
                self.log_telnet = "Download config - Failed"

    def ResetConfig(self,model):
        #Reset all setting

        if "Apresia" in model:
            try:
                lan.sendline("reset config") 
                lan.expect(prompt)
                self.log_telnet = "Reset config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time) 
            except:
                self.log_telnet = "Reset config - Failed"

        elif "Trendnet" in model:
            try:
                lan.sendline("reset config") 
                lan.expect(prompt)
                self.log_telnet = "Reset config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time) 
            except:
                self.log_telnet = "Reset config - Failed"

        elif "ME" in model:
            try:
                lan.sendline("reset config")
                lan.expect("y/n")
                lan.sendline("y")
                lan.expect("Success",timeout=60)
                lan.expect(prompt)
                #lan.sendline("reboot force_agree")
                #lan.expect(prompt)
                self.log_telnet = "Reset config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time) 
            except:
                self.log_telnet = "Reset config - Failed"

        elif "DXS" in model:
            try:
                lan.sendline("reset system") 
                lan.expect("y/n")
                lan.sendline("y")
                lan.expect(prompt)
                self.log_telnet = "Reset config - Passed"
                
                print(colored("\nWaiting for DUT boot up %s sec" %waiting_time ,"yellow"))
                time.sleep(waiting_time) 
            except:
                self.log_telnet = "Reset config - Failed"

    def AccountCreate(self,model):
        #Add account

        if "Apresia" in model:
            try:
                lan.sendline("config account create admin password admin") 
                lan.expect(prompt)
                    
                lan.sendline("save config config_id 1") 
                lan.expect(prompt)
                    
                lan.sendline("logout")
                lan.expect(prompt)
                    
                self.log_telnet = "Add Account - Passed"
                
            except:
                self.log_telnet = "Add Account - Failed"

