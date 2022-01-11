#History
#Security Hole Test item
#




#################################




import re
import os
import sys
import subprocess
import rootfs_boot
import time
import json
import inspect
import pexpect
import glob
from devices import board, wan, lan, wlan, prompt
from lib import installers
from lib.common_telnet import *
from termcolor import *



#-------------General Setting------------

#Remote
ip = '10.0.0.10'
SimpleServer_Port = 8000
kali_path = '/root/Downloads/'

#eth1 = lan
#eth2 = wan
dut_wan_ip = '100.100.100.100'

#local
path = '/home/test/SecurityHole/'
path_result = '/home/test/SecurityHole/result/'
local_ip = '10.0.0.50'


#Device response time for nmap
response_time = '60'
#----------------------------------------


class Security_Device:
    #Connect to Security Hold Test Server

    def Connect_Device(self,ip='10.0.0.10',user='root',pw='123456',port='22'):
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
                    

    def Device_Logout(self):
        #exit the process

        try:
            lan.sendline("exit")
            lan.expect("logout",timeout=10)
            lan.expect(prompt,timeout=10)
            print(colored("\nExit the SecurityHole","yellow"))
        except:
            print(colored("\nUnalbe to Exit the SecurityHole","red"))

    def Start_HttpSimpleServer(self):
        #Start the HttpServer to download the file

        print(colored("\nStarting SimpleHTTPServer","yellow"))
        lan.sendline("python -m SimpleHTTPServer &")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)

    def Stop_HttpSimpleServer(self):
        #Stop the HttpServer

        print(colored("\nStopping SimpleHTTPServer","yellow"))
        lan.sendline("kill -9 $(jobs -p)")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)
    
    def Getfile_Server(self,get_file,save_file):
        # Get testing file to local from Security Hole Test Env
        
        try:
            print(colored("\nGet file from Security Hole Server","yellow"))
            process = pexpect.spawn("wget http://%s:%s/%s -O %s%s" %(ip,SimpleServer_Port,get_file,path,save_file))
            process.logfile_read = sys.stdout
            process.expect('Saving to:')              
        except:
            print(colored("\nError to download the file","red")) 
            msg = "Error to download the file , Skip the Test"
            self.result_message = msg
            raise Exception(msg)
        
class Common:
    #The Module is used by common 
    
    def stop_container(self):
        # stop all container

        print(colored("\nStopping Container...","yellow"))
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)  

    def Loading_DUT_IP(self):
        #load DUT IP from /home/test/SecurityHole/device_info.txt

        global dut_ip,dut_account,dut_password,dut_model
        with open('/home/test/SecurityHole/device_info.txt', 'r') as f:
            line = f.readlines()
            dut_ip = str(line[0]).strip()
            dut_account = str(line[1]).strip()
            dut_password = str(line[2]).strip()
            dut_model = str(line[3]).strip()

        self.stop_container() # Before testing , need to stop all container               
    
    def PingDUT(self):
        #Client Ping DUT

        global ping_dut_result
        j = 0 
        while True:
            lan.sendline("\nclear")
            lan.expect(prompt)
            lan.sendline("ping -c5 -W 1 %s > /tmp/ping_dut.txt" % (dut_ip))
            lan.expect(prompt, timeout=10)
                        
            try:
                lan.sendline("\ncat /tmp/ping_dut.txt |grep received")
                i = lan.expect([' ([0-5]+) (packets )?received','No such file or directory','Network is unreachable'],timeout=10)      
                if i == 0:
                    n = int(lan.match.group(1))
                    lan.expect(prompt)
                    if n > 0:
                        ping_dut_result = 'Pass'
                        print(colored("\nPing DUT OK","yellow"))
                        break
                    else:
                        ping_dut_result = 'Fail'
                        print(colored("\nPing DUT Fail","red"))
                        break

                if i == 1:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow"))
                    if j > 10:
                        break

                if i == 2:
                    j = j + 1
                    print(colored("\nUnable to get IP , Retry %s" %j,"yellow"))
                    if j > 10:
                        break
            except:
                ping_dut_result = 'Fail'
                print(colored("\nPing DUT Fail","red"))
    
    def delete_file(self,delete_path):
        #Delete the local files before testing files

        print(colored("\nDeleting local files if exist...","yellow"))
        
        #delete_path = '/home/test/SecurityHole/*.txt'
        fileList = glob.glob(delete_path)            
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                print(colored("\nError while deleting file","yellow"))
    
    def delete_fileFromRemote(self,delete_folder,delete_fileName):
        #Delete the Remote files before testing files
        
        print(colored("\nDeleting Remote files if exist...","yellow"))
        if delete_folder != 'True':
            lan.sendline("rm -f %s" %(delete_fileName)) 
            lan.expect(prompt)
        else:
            lan.sendline("rm -rf %s*" %(kali_path)) 
            lan.expect(prompt)
            lan.sendline("rm -f %s" %(delete_fileName)) 
            lan.expect(prompt)

class DLINK_Security_HttpLogin_Check(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0006 Pure testing'''

    def __init_(self,match_result):
        
        self.match_result = 'None'

    def weblogin(self):
        #Replace the url and model
        url = "'http://%s'" %dut_ip
        selection = "'%s'" %dut_model
        admin = "'%s'" %dut_account
        passwd = "'%s'" %dut_password

        lan.sendline('sed -i "45c url=%s" weblogin.py' %url) #url
        lan.expect(prompt)
        lan.sendline('sed -i "46c selection=%s" weblogin.py' %selection) #selection
        lan.expect(prompt)
        lan.sendline('sed -i "47c admin=%s" weblogin.py' %admin) #account
        lan.expect(prompt)
        lan.sendline('sed -i "48c passwd=%s" weblogin.py' %passwd) #password
        lan.expect(prompt)
        
        try:
            lan.sendline("python weblogin.py")
            lan.expect('Done',timeout=300)
            lan.expect(prompt)
        except:
            print(colored("\nUnable to weblogin","yellow"))
            self.match_result = 'Unable to weblogin , Failed'
            msg = self.match_result 
            
            #Security_Info = Security_Device()
            #Security_Info.Device_Logout()
            raise Exception (msg)

    def tcpdump(self):
        #Execute the tcpdump and filter the http 80 port
        print(colored("\nStatrting capture packet","yellow"))
        lan.sendline("tcpdump -i eth1 -s 0 -A 'tcp dst port 80 and tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354' and host %s -w httpauth.txt &" %dut_ip)
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)   
    
    def killtcpdump(self):
        #Kill the tcpdump process
        lan.sendline("kill %1")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)
    
    def dump_result(self):
        #Filter the result

        if dut_model == 'DXS' or dut_model == 'ME' or dut_model == 'Apresia' or dut_model == 'Trendnet':
            lan.check_output("cat httpauth.txt |grep -n 'Gambit=\w.*&RPC' -a")            
            match = re.search("Gambit=(\w+)", lan.before)
            
            if dut_password in (match.group(1)):
                self.match_result = 'Packets contained admin_password, Failed'                
            else:
                self.match_result = "<b>Keys Hashed</b></p>" + "<b>gamit=" + (match.group(1)) + "</b>"
        
        elif dut_model == 'DGS':
            lan.check_output("cat httpauth.txt |grep -n 'pelican_ecryp=\w.*%' -a")
            match = re.search("pelican_ecryp=(\w+%)", lan.before)
            
            if dut_password in (match.group(1)):
                self.match_result = 'Packets contained admin_password, Failed'                
            else:
                self.match_result = "<b>Keys Hashed</b></p>" + "<b>pelican_enryp=" + (match.group(1)) + "</b>"
        
        elif dut_model == 'DGS_1100':
            lan.check_output("cat httpauth.txt |grep -n 'pass=\w.*' -a")
            match = re.search("pass=(\w+)", lan.before)
            
            if dut_password in (match.group(1)):
                self.match_result = 'Packets contained admin_password, Failed'                
            else:
                self.match_result = "<b>Keys Hashed</b></p>" + "<b>pelican_enryp=" + (match.group(1)) + "</b>"
        
        elif dut_model == 'EAP':
            lan.check_output("cat httpauth.txt |grep login -a")
            match_admin = re.search("login_name=(\w+)", lan.before)
            match_password = re.search("log_pass=(\w+)", lan.before)
            
            if dut_password in (match_password.group(1)):
                self.match_result = 'Packets contained admin_password, Failed'                
            else:
                self.match_result = "<b>Keys Hashed</b></p>" + "<b>login_name=" + (match_admin.group(1)) + "</b></p>" + "<b>log_pass=" + (match_password.group(1)) + "</b></p>"
        
        elif dut_model == 'Router' or dut_model == 'DAP':
            lan.check_output("cat httpauth.txt |grep -n '<LoginPassword>\w.*</LoginPassword>' -a")
            match_password = re.search("LoginPassword.(\w+)", lan.before)
            
            if dut_password in (match_password.group(1)):
               self.match_result = 'Packets contained admin_password, Failed'                
            else:
               self.match_result = "<b>Keys Hashed</b></p>"  + "<b>login_Password=" + (match_password.group(1)) + "</b></p>"
        
    def runTest(self):
        global msg

        Security_Info = Security_Device()
        Security_Info.Connect_Device()
    
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
        
        if 'Pass' in ping_dut_result:
            self.tcpdump()
            self.weblogin()
            self.killtcpdump()
            self.dump_result()
            Security_Info.Device_Logout()
            
            if 'Failed' in self.match_result:
                msg = self.match_result
                raise Exception (msg)
            else:
                msg = self.match_result
                self.result_message = msg
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_HttpLogin_Check_1(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0006 Backup the cfg and run test''' 
    
    def send_command_check(self,log_telnet1):

        if 'Passed' in log_telnet1: #Send command check                
            pass
        else:
            msg = log_telnet1
            self.result_message = msg
            raise Exception (msg)

    def send_command(self,command):
        #Ctrl the order
        
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        call_telnet = Telnet()
        call_ping = Ping()
        

        if 'save' in command:
            call_telnet.SaveConfig(model=dut_model,id="1")
            log_telnet1 = call_telnet.log_telnet
            call_ping.waiting_dut_bootup(dut_ip=dut_ip)
            self.send_command_check(log_telnet1)
        
        elif 'load' in command:
            call_telnet.LoadConfig(model=dut_model,id="1")
            call_ping.waiting_dut_bootup(dut_ip=dut_ip)
            log_telnet1 = call_telnet.log_telnet
            self.send_command_check(log_telnet1)
                        
        elif 'reset' in command:
            call_telnet.ResetConfig(model=dut_model) 
            call_ping.waiting_dut_bootup(dut_ip=dut_ip)
            log_telnet1 = call_telnet.log_telnet
            self.send_command_check(log_telnet1)
                    
    def runTest(self):
        
        #Step 1 : Telnet to DUT
        #Step 2 : Backup config to tftp
        #Step 3 : Reset
        #Step 4 : Run Weblogin / Tcp dump
        #Step 5 : Download config to DUT
        #Step 6 : Result

        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
                
        if 'Pass' in ping_dut_result:
            Common_info = Common()
            Common_info.Loading_DUT_IP()        
                               
            call_telnet = Telnet()
            if 'Router' in dut_model or 'DAP' in dut_model or 'EAP' in dut_model:
                pass
            else:
                call_telnet.Connect_telnet(host=dut_ip,username=dut_account,password=dut_password)
                self.send_command(command='save')
                
                call_telnet.Connect_telnet(host=dut_ip,username=dut_account,password=dut_password)
                self.send_command(command='reset')                
                
                #Add if reset , Apresia switch will return to "adpro" of account
                if dut_model == 'Apresia':
                    if dut_account == 'admin':
                        call_telnet.Connect_telnet(host=dut_ip,username="adpro",password="")
                        call_telnet.AccountCreate(model=dut_model)
                else:
                    pass

                http_check = DLINK_Security_HttpLogin_Check(None)
                http_check.runTest()
                                
                msg = http_check.match_result
                self.result_message = msg

                call_telnet.Connect_telnet(host=dut_ip,username=dut_account,password=dut_password)
                self.send_command(command='load')        
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            self.result_message = msg
            raise Exception (msg)
    
    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_Nmap_TCPSyn_Scan(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0003'''
    
    def result(self,open_ports):
        global msg

        if status == 'opened':
            msg = " Found %s open TCP ports : <b>%s</b>  " % \
                (len(open_ports), ", ".join(open_ports))
        
        elif status == 'closed':
            msg = " Found %s closed TCP ports : <b>%s</b>  " % \
                (len(open_ports), ", ".join(open_ports))
        
        elif status == 'filtered':
            msg = " Found %s filtered TCP ports : <b>%s</b>  " % \
                (len(open_ports), ", ".join(open_ports))
        
        return msg
    
    def main(self,interface):
        #Nmap scan TCPSyn
        global status
        global msg
        
        lan.sendline('nmap -sS -e %s -v -p 1-65535 -T5 --min-rate 500 --max-retries 1 %s | tee nmap.txt' %(interface,dut_ip))
        lan.expect('Starting Nmap')
        for i in range(3600):
            if 0 == lan.expect(['Nmap scan report', pexpect.TIMEOUT], timeout=3600):
                break
            lan.sendcontrol('c')
            lan.expect(prompt)
            time.sleep(1)
        lan.expect(prompt, timeout=60)
        
        #Filter result
        lan.check_output("cat nmap.txt |grep '^[1-99999]'")                        
        #Check the value if open / closed / filtered or nothing
        if 'open' in lan.before:
            open_ports = re.findall("(\d+)\/tcp\s+open", lan.before)  
            status = 'opened'
            self.result(open_ports)

        elif 'closed' in lan.before:
            open_ports = re.findall("(\d+)\/tcp\s+closed", lan.before)  
            status = 'closed'
            self.result(open_ports)
        
        elif 'filtered' in lan.before:
            open_ports = re.findall("(\d+)/tcp\s+filtered", lan.before)     
            status = 'filtered'
            self.result(open_ports)
            
        else:
            msg = " <b>All port are closed</b> "
    
    def runTest(self):
        global msg

        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
        
        if 'Pass' in ping_dut_result:     
            self.main(interface='eth1')                           
            Security_Info.Device_Logout()
            
            if 'closed' in msg:
                self.result_message = msg
            else:                
                self.result_message = msg
                raise Exception (msg)
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            self.result_message = msg
            raise Exception (msg)
    
    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_Nmap_TCPSyn_Scan_WAN(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0003'''

    def runTest(self):
        global dut_ip
        global msg

        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
                
        if 'Pass' in ping_dut_result:
            #Load TCPSyn
            dut_ip = dut_wan_ip
            TCPsyn = DLINK_Security_Nmap_TCPSyn_Scan(None)
            TCPsyn.main(interface='eth2')  
            Security_Info.Device_Logout()
            
            if 'closed' in msg:
                self.result_message = msg
            else:                
                self.result_message = msg
                raise Exception (msg)
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            Security_Info.Device_Logout()
            self.result_message = msg
            raise Exception (msg) 
            
            
    def recover(self):
        board.sendcontrol(']')


class DLINK_Security_Nmap_TCPFin_Scan(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0008'''
   
    def result(self,open_ports):
        global msg

        if status == 'opened':
            msg = " Found %s open TCP ports : <b>%s</b>  " % \
                (len(open_ports), ", ".join(open_ports))
        
        elif status == 'closed':
            msg = " Found %s closed TCP ports : <b>%s</b>  " % \
                (len(open_ports), ", ".join(open_ports))
        
        elif status == 'filtered':
            msg = " Found %s filtered TCP ports : <b>%s</b>  " % \
                (len(open_ports), ", ".join(open_ports))
        
        return msg

    def main(self,interface):
        #Nmap scan TCPFin scan
        global msg
        global status

        lan.sendline('nmap -sF -e %s -v -p 1-65535 -T5 %s | tee nmap.txt' %(interface,dut_ip))
        lan.expect('Starting Nmap')
        for i in range(3600):
            if 0 == lan.expect(['Nmap scan report', pexpect.TIMEOUT], timeout=3600):
                break
            lan.sendcontrol('c')
            lan.expect(prompt)
            time.sleep(1)
        lan.expect(prompt, timeout=60)

        #Filter result
        lan.check_output("cat nmap.txt |grep '^[1-99999]'")                        
        #Check the value if open / closed / filtered or nothing
        if 'open' in lan.before:
            open_ports = re.findall("(\d+)\/tcp\s+open", lan.before)  
            status = 'opened'
            self.result(open_ports)

        elif 'closed' in lan.before:
            open_ports = re.findall("(\d+)\/tcp\s+closed", lan.before)  
            status = 'closed'
            self.result(open_ports)
        
        elif 'filtered' in lan.before:
            open_ports = re.findall("(\d+)/tcp\s+filtered", lan.before)     
            status = 'filtered'
            self.result(open_ports)
            
        else:
            msg = " <b>All port are closed</b> "
 
    def runTest(self):
        global msg

        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
        
        if 'Pass' in ping_dut_result:     
            self.main(interface='eth1')                           
            Security_Info.Device_Logout()
        
            if 'open' in msg:
                self.result_message = msg
                raise Exception (msg)
            else:                
                self.result_message = msg

        else:
            n = 0
            while True:
                print(colored("\nWaiting for device response for %s" % response_time ,"yellow"))
                time.sleep(int(response_time))
                Common_info.PingDUT()
                if 'Pass' in ping_dut_result:
                    self.main(interface='eth1')                           
                    Security_Info.Device_Logout()
        
                    if 'open' in msg:
                        self.result_message = msg
                        raise Exception (msg)
                        break
                    else:                
                        self.result_message = msg
                        break
                else:
                    n += 1
                    if n > 5:
                        pass
            
            if 'Pass' in ping_dut_result: 
                pass
            else:
                msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
                self.result_message = msg
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_Nmap_TCPFin_Scan_WAN(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0008'''

    def runTest(self):
        global dut_ip
        global msg

        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
                
        if 'Pass' in ping_dut_result:
            #Load TCPFin
            dut_ip = dut_wan_ip
            TCPFin = DLINK_Security_Nmap_TCPFin_Scan(None)
            TCPFin.main(interface='eth2')  
            Security_Info.Device_Logout()
            
            if 'open' in msg:
                self.result_message = msg
                raise Exception (msg)
            else:                
                self.result_message = msg
        else:
            n = 0
            while True:
                print(colored("\nWaiting for device response for %s" % response_time ,"yellow"))
                time.sleep(int(response_time))
                Common_info.PingDUT()
                if 'Pass' in ping_dut_result:
                    self.main(interface='eth1')                           
                    Security_Info.Device_Logout()
        
                    if 'open' in msg:
                        self.result_message = msg
                        raise Exception (msg)
                        break
                    else:                
                        self.result_message = msg
                        break
                else:
                    n += 1
                    if n > 5:
                        pass
            
            if 'Pass' in ping_dut_result: 
                pass
            else:
                msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
                self.result_message = msg
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_Nmap_UDP_Scan(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0007'''
    
    def result(self,open_ports):
        global msg
        
        if status == 'opened':
            msg = " Found %s open UDP ports : <b>%s</b>  " % \
            (len(open_ports), ", ".join(open_ports))
        
        elif status == 'closed':
            msg = " Found %s closed UDP ports : <b>%s</b>  " % \
            (len(open_ports), ", ".join(open_ports))
        
        elif status == 'filtered':
            msg = " Found %s filtered UDP ports : <b>%s</b>  " % \
            (len(open_ports), ", ".join(open_ports))
        
        return msg
        
    
    def main(self,interface):
        #Nmap scan UDP scan
        #Too speed up the nmap for udp , --min-rate 500 / --max-retries 1
        global status
        global msg

        lan.sendline('nmap -sU -e %s -v -p 1-65535 -T5 --min-rate 500 --max-retries 1 %s | tee nmap.txt' %(interface,dut_ip))
        lan.expect('Starting Nmap')
        for i in range(3600):
            if 0 == lan.expect(['Nmap scan report', pexpect.TIMEOUT], timeout=3600):
                break
            lan.sendcontrol('c')
            lan.expect(prompt)
            time.sleep(1)
        lan.expect(prompt, timeout=60)
        
        #Filter result
        lan.check_output("cat nmap.txt |grep '^[1-99999]'")                        
        #Check the value if open / closed / filtered or nothing
        if 'open' in lan.before:
            open_ports = re.findall("(\d+)\/udp\s+open", lan.before)  
            status = 'opened'
            self.result(open_ports)

        elif 'closed' in lan.before:
            open_ports = re.findall("(\d+)\/udp\s+closed", lan.before)  
            status = 'closed'
            self.result(open_ports)
        
        elif 'filtered' in lan.before:
            open_ports = re.findall("(\d+)/udp\s+filtered", lan.before)     
            status = 'filtered'
            self.result(open_ports)
            
        else:
            msg = " <b>All port are closed</b> "
    
    def runTest(self):
        global msg

        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
        
        if 'Pass' in ping_dut_result:     
            self.main(interface='eth1')                           
            Security_Info.Device_Logout()
            
            if 'closed' in msg:
                self.result_message = msg
            else:                
                self.result_message = msg
                raise Exception (msg)
        else:
            n = 0
            while True:
                print(colored("\nWaiting for device response for %s" % response_time ,"yellow"))
                time.sleep(int(response_time))
                Common_info.PingDUT()
                if 'Pass' in ping_dut_result:
                    self.main(interface='eth1')                           
                    Security_Info.Device_Logout()
        
                    if 'closed' in msg:
                        self.result_message = msg
                        break
                    else:                
                        self.result_message = msg
                        raise Exception (msg)
                        break
                else:
                    n += 1
                    if n > 5:
                        pass
            
            if 'Pass' in ping_dut_result: 
                pass
            else:
                msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
                self.result_message = msg
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_Nmap_UDP_Scan_WAN(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0007'''

    def runTest(self):       
        global dut_ip
        global msg

        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
                
        if 'Pass' in ping_dut_result:
            #Load UDP Scan
            dut_ip = dut_wan_ip
            UDPscan = DLINK_Security_Nmap_UDP_Scan(None)
            UDPscan.main(interface='eth2')  
            Security_Info.Device_Logout() 
                          
            if 'closed' in msg:
                self.result_message = msg
            else:                
                self.result_message = msg
                raise Exception (msg)
        else:
            n = 0
            while True:
                print(colored("\nWaiting for device response for %s" % response_time ,"yellow"))
                time.sleep(int(response_time))
                Common_info.PingDUT()
                if 'Pass' in ping_dut_result:
                    self.main(interface='eth1')                           
                    Security_Info.Device_Logout()
        
                    if 'closed' in msg:
                        self.result_message = msg
                        break
                    else:                
                        self.result_message = msg
                        raise Exception (msg)
                        break
                else:
                    n += 1
                    if n > 5:
                        pass
            
            if 'Pass' in ping_dut_result: 
                pass
            else:
                msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
                self.result_message = msg
                raise Exception (msg)
       
    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_SSH_Vulnetability(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0004'''

    def start_container(self):
        #Start container with ruby test environment
    
        print(colored("\nStarting ruby container...","yellow"))
        
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt) 
        lan.sendline("docker run --net=host --name lan --privileged -it ruby:193 /bin/bash")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)

    def stop_container(self):
        #Stop container with ruby test environment
    
        print(colored("\nStopping ruby container...","yellow"))
        lan.sendline("exit")
        lan.expect(prompt)
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)


    def check_dut_status(self):
        #Check DUT is alive
        global dut_status
        try:
            print(colored("\nChecking DUT status , Waiting...","yellow"))
            lan.sendline("ping -c5 -W 1 %s " % (dut_ip))
            lan.expect("5 (packets )?received", timeout=30)
            lan.expect(prompt)   
            dut_status = 'Passed'
        except:
            print(colored("\nDUT is down , Failed...","yellow"))
            dut_status = 'Failed'

    def waiting_dut(self):
        #Waiting dut to run the next test
        n = 0
        while True:
            try:
                print(colored("\nChecking for DUT status , Waiting to the next test...","yellow"))
                lan.sendline("ping -c5 -W 1 %s " % (dut_ip))
                lan.expect("5 (packets )?received", timeout=30)
                lan.expect(prompt)
                print(colored("\nDUT is alive...","yellow"))
                break
            except:
                print(colored("\nDUT is down , Waiting for DUT is up...","red"))
                n += 1
                if n > 20:
                    msg = 'Unable to connect to DUT over 20 times'
                    self.result_message = msg
                    raise Exception (msg)
                    break

    def case_check(self):
        #check the case

        global case_result,dut_status
        try:
            i = lan.expect(['connection established','Connection refused'],timeout=15)
            if i == 0:
                lan.expect(prompt,timeout=30)
                self.check_dut_status()
                case_result = 'Passed'
            if i == 1:
                lan.expect(prompt,timeout=30)
                self.check_dut_status()
                case_result = 'Passed'
        except: 
            lan.sendcontrol('c')
            lan.expect(prompt,timeout=30)
            dut_status = 'Passed'
            case_result = 'Failed'

    def case(self):
        
        #----------Define the case command-----------
        case1 = 'auth_req'
        case2 = 'global_req'
        case3 = 'ch_win'
        case4 = 'ch_eof'
        case5 = 'ch_open'
        case6 = 'ch_close'
        case7 = 'ch_req'
        case8 = 'ch_req2' 
        #-------------------------------------------
        
        #case1
        print(colored("\nStarting Case1...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case1))
        self.case_check()
 
        if 'Passed' in dut_status:  
            case1_result_msg = '<b>%s</b> = %s' % (case1,dut_status)    
        else:
            case1_result_msg = '<b>%s</b> = Unable to establish to %s' % (case1,dut_ip)
        
        
        self.waiting_dut()
        
        #case2
        print(colored("\nStarting Case2...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case2))
        self.case_check()
               
        if 'Passed' in dut_status:  
            case2_result_msg = '<b>%s</b> = %s' % (case2,dut_status)    
        else:
            case2_result_msg = '<b>%s</b> = Unable to establish to %s' % (case2,dut_ip)

        self.waiting_dut()
        
        #case3
        print(colored("\nStarting Case3...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case3))
        self.case_check()      
        
        if 'Passed' in dut_status:  
            case3_result_msg = '<b>%s</b> = %s' % (case3,dut_status)    
        else:
            case3_result_msg = '<b>%s</b> = Unable to establish to %s' % (case3,dut_ip)
        
        self.waiting_dut()
        
        #case4
        print(colored("\nStarting Case4...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case4))
        self.case_check()     
        
        if 'Passed' in dut_status:  
            case4_result_msg = '<b>%s</b> = %s' % (case4,dut_status)    
        else:
            case4_result_msg = '<b>%s</b> = Unable to establish to %s' % (case4,dut_ip)
        
        self.waiting_dut()
        
        #case5
        print(colored("\nStarting Case5...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case5))
        self.case_check()      
        
        if 'Passed' in dut_status:  
            case5_result_msg = '<b>%s</b> = %s' % (case5,dut_status)    
        else:
            case5_result_msg = '<b>%s</b> = Unable to establish to %s' % (case5,dut_ip)
        
        self.waiting_dut()
        
        #case6
        print(colored("\nStarting Case6...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case6))
        self.case_check()        
        
        if 'Passed' in dut_status:  
            case6_result_msg = '<b>%s</b> = %s' % (case6,dut_status)    
        else:
            case6_result_msg = '<b>%s</b> = Unable to establish to %s' % (case6,dut_ip)
        
        self.waiting_dut()
        
        #case7
        print(colored("\nStarting Case7...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case7))
        self.case_check()
        
        if 'Passed' in dut_status :  
            case7_result_msg = '<b>%s</b> = %s' % (case7,dut_status)    
        else:
            case7_result_msg = '<b>%s</b> = Unable to establish to %s' % (case7,dut_ip)
        
        self.waiting_dut()
        
        #case8
        print(colored("\nStarting Case8...","yellow"))
        lan.sendline("ruby sshvul.rb %s %s %s %s" %(dut_ip,dut_account,dut_password,case8))
        self.case_check()
        
        if 'Passed' in dut_status:  
            case8_result_msg = '<b>%s</b> = %s' % (case8,dut_status)    
        else:
            case8_result_msg = '<b>%s</b> = Unable to establish to %s' % (case8,dut_ip)
        
        self.waiting_dut()

        #Write the Result
        msg = case1_result_msg + '<p>' + case2_result_msg + '<p>' + case3_result_msg + '<p>' + case4_result_msg + '<p>' + case5_result_msg + '<p>' + case6_result_msg + '<p>' + case7_result_msg + '<p>' + case8_result_msg
        
        if 'Unable' in msg:            
            self.result_message = msg
            raise Exception (msg)
        else:
            self.result_message = msg

            
    def runTest(self):       
        Security_Info = Security_Device()
        Security_Info.Connect_Device()
    
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
        
        if 'Pass' in ping_dut_result:     
            self.start_container()
            self.case()
            self.stop_container()            
            Security_Info.Device_Logout() 
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            self.result_message = msg
            raise Exception (msg)
    
    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_Web_Vulnetability(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0005 Pure Testing'''
    
    def __init_(self,match_result):
        
        self.match_result = 'None'


    def curl_httpResponse(self):
        #Check http response code
        #Reserve the function due to unable to reproduce

        global browse_webui_result
        lan.sendline("curl -s -o /dev/null -w '%{http_code}' https://%s " %(dut_ip))
        try: 
            lan.expect('200')
            lan.expect(prompt)
            browse_webui_result = 'Passed'
        except:
            browse_webui_result = 'Failed'
        
    def case_check(self):
        #Check the case
        #If timeout > 30sec , skip the test

        global case_web_result
        try:
            i = lan.expect(['HTTPBadResponse','HTTP/1.1 302','HTTP/1.1 400','HTTP/1.1 404','HTTP/1.1 302','HTTP/1.1 403'],timeout=10)
            if i < 6 :
                lan.expect(prompt,timeout=30)
                case_web_result = 'Passed'
        except:
            lan.sendcontrol('c')
            lan.expect(prompt,timeout=30)
            case_web_result = 'Passed'


    def case(self):     
        global case1_web_result,case2_web_result,case3_web_result
                    
        #case1
        lan.sendline("ruby DES-3852_http_referer_exploit.rb %s 80 1" %(dut_ip))
        self.case_check()
        case1_web_result = case_web_result

        if 'Passed' in case1_web_result:  
            case1_web_result_msg = '<b>case1</b> = %s' % (case1_web_result)    
        else:
            case1_web_result_msg = '<b>case1</b> = %s'  (case1_web_result)

        #case2
        lan.sendline("ruby DES-3852_http_referer_exploit.rb %s 80 2" %(dut_ip))
        self.case_check()
        case2_web_result = case_web_result                   
        
        if 'Passed' in case2_web_result:  
            case2_web_result_msg = '<b>case2</b> = %s' % (case2_web_result)    
        else:
            case2_web_result_msg = '<b>case2</b> = %s'  (case2_web_result)

        #case3
        lan.sendline("ruby DES-3852_http_referer_exploit.rb %s 80 3" %(dut_ip))
        self.case_check()
        case3_web_result = case_web_result                   
        
        if 'Passed' in case3_web_result:  
            case3_web_result_msg = '<b>case3</b> = %s' % (case3_web_result)    
        else:
            case3_web_result_msg = '<b>case3</b> = %s'  (case3_web_result)

        #Write the Result
        self.match_result = case1_web_result_msg + '<p>' + case2_web_result_msg + '<p>' + case3_web_result_msg
        
        msg = self.match_result

        if 'Failed' in msg:            
            self.result_message = msg
            raise Exception (msg)
        else:
            self.result_message = msg

    def runTest(self):
        
        Security_Info = Security_Device()
        Security_Info.Connect_Device()
    
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
        
        if 'Pass' in ping_dut_result:
            Load_container = DLINK_Security_SSH_Vulnetability(None)
            Load_container.start_container()
            self.case()
            Load_container.stop_container()            
            Security_Info.Device_Logout() 
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_Web_Vulnetability_1(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0005 Backup config / reset and run the testing'''

    def send_command_check(self,log_telnet1):

        if 'Passed' in log_telnet1: #Send command check                
            pass
        else:
            msg = log_telnet1
            self.result_message = msg
            raise Exception (msg)

    def send_command(self,command):
        #Ctrl the order
        
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        call_telnet = Telnet()
        call_ping = Ping()
        

        if 'save' in command:
            call_telnet.SaveConfig(model=dut_model,id="1")
            log_telnet1 = call_telnet.log_telnet
            call_ping.waiting_dut_bootup(dut_ip=dut_ip)
            self.send_command_check(log_telnet1)
        
        elif 'load' in command:
            call_telnet.LoadConfig(model=dut_model,id="1")
            call_ping.waiting_dut_bootup(dut_ip=dut_ip)
            log_telnet1 = call_telnet.log_telnet
            self.send_command_check(log_telnet1)
                        
        elif 'reset' in command:
            call_telnet.ResetConfig(model=dut_model) 
            call_ping.waiting_dut_bootup(dut_ip=dut_ip)
            log_telnet1 = call_telnet.log_telnet
            self.send_command_check(log_telnet1)

    def runTest(self):

        #Step 1 : Telnet to DUT
        #Step 2 : Backup config to tftp
        #Step 3 : Reset
        #Step 4 : Run web Vulnetability
        #Step 5 : Download config to DUT
        #Step 6 : Result

        Common_info = Common()
        Common_info.Loading_DUT_IP()
        Common_info.PingDUT()
                
        if 'Pass' in ping_dut_result:
            Common_info = Common()
            Common_info.Loading_DUT_IP()        
                               
            call_telnet = Telnet()
            if 'Router' in dut_model or 'DAP' in dut_model or 'EAP' in dut_model:
                pass
            else:
                call_telnet.Connect_telnet(host=dut_ip,username=dut_account,password=dut_password)
                self.send_command(command='save')
                
                call_telnet.Connect_telnet(host=dut_ip,username=dut_account,password=dut_password)
                self.send_command(command='reset')                
                
                web_check = DLINK_Security_Web_Vulnetability (None)
                web_check.runTest()
                
                msg = web_check.match_result
                self.result_message = msg

                call_telnet.Connect_telnet(host=dut_ip,username=dut_account,password=dut_password)
                self.send_command(command='load')        
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            self.result_message = msg
            raise Exception (msg)
        
        
    def recover(self):
        board.sendcontrol(']')






class DLINK_Security_FwProtection_Analysis(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0013'''

    def getFileName(self):
        global find_model,fw_name
        
        dir = "/tftpboot/security/"
        for root, dirs, files in os.walk(dir):
            for file in files:
                find_model = os.path.join(root,file)
        
        Common_info = Common()
        Common_info.delete_file(delete_path = '/tftpboot/*.hex')
        Common_info.delete_file(delete_path = '/tftpboot/*.bin')
        Common_info.delete_file(delete_path = path + 'fw_protection_error.txt')
        fw_name = find_model.replace(dir,"")

        import shutil
        #Copyfile to /tftpboot
        shutil.copy(find_model,"/tftpboot/")
        
    def tftp_getFileFromLocal(self):
        #Connect to security and get file from local
        Common_info = Common()
        Common_info.delete_fileFromRemote(delete_folder='True',delete_fileName='fw_protection_error.txt')           
                
        lan.sendline("cd Downloads/")
        lan.expect(prompt)
        
        lan.sendline("tftp %s" %local_ip)
        lan.expect("tftp> ")
        lan.sendline("binary")
        lan.expect("tftp> ")
        lan.sendline("get %s" %fw_name)
        lan.expect("tftp> ",timeout=30)
        lan.sendline("quit")
        lan.expect(prompt)
  
    def write_result(self):
        #Read file and output
        Security_Info = Security_Device()
        
        
        if fw_find_files_error is None:
            print(colored("\nPass , Not found Extracted files" , "yellow"))
            self.result_message = fw_name + ' = Passed'
        else:    
            with open('%sfw_protection_error.txt' %(path), 'r' ) as f:
                read_file = f.read().replace(kali_path,'')
                read_file_transfer = read_file.split()

                if 'etc' in read_file:
                    msg =  "<b>" + fw_name + " = Failed </b><p>" + "<p>".join(read_file_transfer)
                    self.result_message = msg
                    Security_Info.Stop_HttpSimpleServer()
                    Security_Info.Device_Logout()
                    raise Exception("Error to Find etc of Extracted Files , Please check the test result")
                
                elif 'bin' in read_file:
                    msg = "<b>" + fw_name + "</b><p>" + "<p>".join(read_file_transfer)
                    self.result_message = msg
                    Security_Info.Stop_HttpSimpleServer()
                    Security_Info.Device_Logout()
                    raise Exception("Error to Find bin of Extracted Files , Please check the test result")
                
                elif 'sbin' in read_file:
                    msg = "<b>" + fw_name + "</b><p>" + "<p>".join(read_file_transfer)
                    self.result_message = msg
                    Security_Info.Stop_HttpSimpleServer()
                    Security_Info.Device_Logout()
                    raise Exception("Error to Find sbin of Extracted Files , Please check the test result")
                
                elif 'conf' in read_file:
                    msg = "<b>" + fw_name + "</b><p>" + "<p>".join(read_file_transfer)
                    self.result_message = msg
                    Security_Info.Stop_HttpSimpleServer()
                    Security_Info.Device_Logout()
                    raise Exception("Error to Find conf of Extracted Files , Please check the test result")
                
                #DGS-1100-08V2 failed result
                elif 'dbg' in read_file or 'gif' in read_file or 'bmp' or 'ico' in read_file:
                    msg = "<b>" + fw_name + "</b><p>" + "<p>".join(read_file_transfer)
                    self.result_message = msg
                    Security_Info.Stop_HttpSimpleServer()
                    Security_Info.Device_Logout()
                    raise Exception("Error to Find conf of Extracted Files , Please check the test result")
                else:
                    #fw_find_files_error = None
                    print(colored("\nNot found invalid files , Passed" , "yellow"))
                    Security_Info.Stop_HttpSimpleServer()
                    Security_Info.Device_Logout()

    def check_folderEncryped(self):
        global fw_find_files_error , kali_path , fw_path
        #Step 1 = Check Folder is created or not
        #Step 2 = 1.Check some files inside and everything is encrypted
        #         2.If some files inside , should not contain bin , etc ,sbin or other files
        
        print(colored("\nStarting binwalk for searching the %s" %fw_name,"yellow"))
        lan.sendline("binwalk -Me %s%s" %(kali_path,fw_name))
        lan.expect("Scan Time:")
        lan.expect(prompt,timeout=120)

        fw_extracted = '_' + fw_name + '.extracted'        
        fw_path = kali_path + fw_extracted
        
        lan.sendline("ls %s" %fw_path)
        i = lan.expect(["No such file or directory"] + prompt,timeout=10)
        if i == 0:
            fw_find_files_error = None
            self.write_result()
        else:
            print(colored("\nFound extracted folder ,Checking..." , "red"))
            fw_find_files_error = 'True'
            lan.sendline("cd /root/")
            lan.expect(prompt)
            lan.sendline("find %s  > fw_protection_error.txt" %fw_path)
            lan.expect(prompt)    
            Security_Info = Security_Device()
            Security_Info.Getfile_Server(get_file='fw_protection_error.txt',save_file='fw_protection_error.txt')       
            self.write_result()   
                
            
    def runTest(self):       
        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Security_Info.Stop_HttpSimpleServer()
        Security_Info.Start_HttpSimpleServer()

        self.getFileName()
        self.tftp_getFileFromLocal()     
        self.check_folderEncryped()
        
        
    def recover(self):
        board.sendcontrol(']')

class DLINK_Security_SSLScan(rootfs_boot.RootFSBootTest):
    '''DKP1702002-0015'''

    def ssl_scanner(self,scan_tls10_file='tls10.txt',scan_tls11_file='tls11.txt',scan_tls12_file='tls12.txt'):
        # ssl_scanner v1  
        scan_ssl2_file = 'ssl2.txt'
        scan_ssl3_file = 'ssl3.txt'
        try:
            print(colored("\nScanning %s to TCP on 443" %dut_ip,"yellow"))
            
            #Remove previous file
            lan.sendline("rm -f ssl*")
            lan.expect(prompt)
            lan.sendline("rm -f ttl*")
            lan.expect(prompt)
            
            #Scan Tls
            lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --tls10 %s:443 |col -b > %s" %(dut_ip,scan_tls10_file))
            idx = lan.expect(["socket.error"] + prompt,timeout=30)
            if idx == 0:
                #Fail Response
                lan.sendline("\n\n\n")
                lan.expect(prompt)
                print(colored("\nError response on %s TCP on 443" %dut_ip,"yellow"))
                msg = "%s does not response to TCP on 443" %dut_ip
                self.result_message = msg
                raise Exception(msg)
            else:
                #Pass Response   
                lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --tls11 %s:443 |col -b > %s" %(dut_ip,scan_tls11_file))
                lan.expect(prompt)
                lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --tls12 %s:443 |col -b > %s" %(dut_ip,scan_tls12_file))
                lan.expect(prompt)
        
                #Scan SSL        
                lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --ssl2 %s:443 |col -b > %s" %(dut_ip,scan_ssl2_file))
                lan.expect(prompt)
                lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --ssl3 %s:443 |col -b > %s" %(dut_ip,scan_ssl3_file))
                lan.expect(prompt)

                #Remove special character
                lan.sendline("sed -i 's/0m//g' %s" %scan_tls10_file)
                lan.expect(prompt)
                lan.sendline("sed -i 's/0m//g' %s" %scan_tls11_file)
                lan.expect(prompt)
                lan.sendline("sed -i 's/0m//g' %s" %scan_tls12_file)
                lan.expect(prompt)
        
                lan.sendline("sed -i 's/0m//g' %s" %scan_ssl2_file)
                lan.expect(prompt)
                lan.sendline("sed -i 's/0m//g' %s" %scan_ssl3_file)
                lan.expect(prompt)
        except:
            print(colored("\nError response on %s TCP on 443" %dut_ip,"yellow"))
            msg = "%s does not response to TCP on 443" %dut_ip
            raise Exception(msg)


    def check_scanner2(self):
        #ssl_scanner v2
        #Check command can be out the file or not support
        
        idx = lan.expect(["socket.error"] + prompt,timeout=30)
        if idx == 0:
            #Fail Response
            lan.sendline("\n\n\n")
            lan.expect(prompt)
            print(colored("\nError response on %s TCP on 443" %dut_ip,"yellow"))
            msg = "%s does not response to TCP on 443" %dut_ip
            self.result_message = msg
        else:
            #Check Response
            try:
                lan.sendline("\n\n\n")
                lan.expect(prompt,timeout=5)
            except:
                lan.sendcontrol('c')
                Security_Info = Security_Device()
                Security_Info.Device_Logout()
                print(colored("\nCommand is skip","yellow"))
                msg = "%s does not response to TCP on 443 , Please check your DUT setting , or not enabled the 443 port" %dut_ip
                self.result_message = msg
                raise Exception(msg)

    def ssl_scanner2(self):
        #ssl_scanner v2
        scan_tls10_file = 'tls10.txt'
        scan_tls11_file = 'tls11.txt'
        scan_tls12_file= 'tls12.txt'
        scan_ssl2_file = 'ssl2.txt'
        scan_ssl3_file = 'ssl3.txt'
        
        print(colored("\nScanning %s to TCP on 443" %dut_ip,"yellow"))
            
        #Remove previous file
        lan.sendline("rm -f ssl*")
        lan.expect(prompt)
        lan.sendline("rm -f ttl*")
        lan.expect(prompt)
            
        #Scan Tls 
        lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --tls10 %s:443 |col -b > %s" %(dut_ip,scan_tls10_file))
        self.check_scanner2() 
        lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --tls11 %s:443 |col -b > %s" %(dut_ip,scan_tls11_file))
        self.check_scanner2()
        lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --tls12 %s:443 |col -b > %s" %(dut_ip,scan_tls12_file))   
        self.check_scanner2() 
        
        #Scan SSL
        lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --ssl2 %s:443 |col -b > %s" %(dut_ip,scan_ssl2_file))
        self.check_scanner2()
        lan.sendline("\npysslscan scan --scan=server.ciphers --report=term --ssl3 %s:443 |col -b > %s" %(dut_ip,scan_ssl3_file))
        self.check_scanner2()

        #Remove special character
        lan.sendline("sed -i 's/0m//g' %s" %scan_tls10_file)
        lan.expect(prompt)
        lan.sendline("sed -i 's/0m//g' %s" %scan_tls11_file)
        lan.expect(prompt)
        lan.sendline("sed -i 's/0m//g' %s" %scan_tls12_file)
        lan.expect(prompt)
        
        lan.sendline("sed -i 's/0m//g' %s" %scan_ssl2_file)
        lan.expect(prompt)
        lan.sendline("sed -i 's/0m//g' %s" %scan_ssl3_file)
        lan.expect(prompt)



    def getfile_tls(self):
        # Get TLS source file to local from Security Hole Test Env
        try:
            print(colored("\nGet SSL file from Security Hole Server","yellow"))
            for i in range(3):
                process = pexpect.spawn("wget http://%s:%s/tls1%s.txt -O %stls1%s.txt" %(ip,SimpleServer_Port,i,path,i))
                process.logfile_read = sys.stdout
                process.expect('Saving to:')
        except:
            print(colored("\nError to download the TLS file","red"))
                
    def getfile_ssl(self,ssl_file):
        # Get SSL source file to local from Security Hole Test Env
        try: 
            process = pexpect.spawn("wget http://%s:%s/%s.txt -O %s%s.txt" %(ip,SimpleServer_Port,ssl_file,path,ssl_file))
            process.logfile_read = sys.stdout
            process.expect('Saving to:')
        except:
            print(colored("\nError to download the SSL file","red"))

    def ssl_filter_pass_output(self,tls_pass,tls_file):
        #Filter output pass result to file
        
        if tls_pass is None:
            pass
        else:
            with open('%s%s_find_pass_filter.txt' %(path,tls_file), 'a+' ) as f:
                f.write("%s\n" % tls_pass)
    
    def ssl_filter_fail_output(self,tls_fail,tls_file):
        #Filter output fail result to file
    
        if tls_fail is None:
            pass
        else:
            with open('%s%s_find_fail_filter.txt' %(path,tls_file), 'a+' ) as f:
                f.write("%s\n" % tls_fail)

    def ssl_filter_main(self,tls_file):
        #Read SSL/TLS file and filter result
        #Defind the value
        #Filter Accepted from file
        
        with open('%s%s.txt' %(path,tls_file), 'r' ) as f:
            ssl_scan_result = f.read()
        
        if 'Accepted' in ssl_scan_result:
            #Check scan result
            #Filter the key word of TLS_ and SSL_
            if 'tls' in tls_file:
                #Filter tls
                ssl_result_filter = re.findall('(TLS_.*)',ssl_scan_result)
                print(colored("\nFound scan result of %s , Starting to filter" %tls_file,"yellow"))
            else:
                #Filter ssl
                ssl_result_filter = re.findall('(SSL_.*)',ssl_scan_result)
                print(colored("\nFound scan result of %s , Starting to filter" %tls_file,"yellow"))
            
            #Check vaild in algorithms
            valid_algorithms = ['_SHA256','_SHA384','_SHA512']
                 
            for ssl_result in ssl_result_filter:            
                #Compare the value from the ssl_result
                tls_pass = None
                tls_fail = None
                i = 0
            
                #Check Criteria
                if valid_algorithms[i] in ssl_result:#0
                    if valid_algorithms[i+1] in ssl_result:#1                    
                        if valid_algorithms[i+2] in ssl_result:#2
                            tls_fail = ssl_result
                            self.ssl_filter_fail_output(tls_fail,tls_file)
                            #print 'bb1'
                        else:
                            tls_pass = ssl_result
                            self.ssl_filter_pass_output(tls_pass,tls_file)
                            #print 'bb2'
                    else:
                        if valid_algorithms[i+2] in ssl_result:#2
                            tls_fail = ssl_result
                            self.ssl_filter_fail_output(tls_fail,tls_file)
                            #print 'bb3'
                        else:
                            tls_pass = ssl_result
                            self.ssl_filter_pass_output(tls_pass,tls_file)
                            #print 'bb4'
                else:
                    if valid_algorithms[i+1] in ssl_result:#1
                        if valid_algorithms[i+2] in ssl_result:#2
                            tls_pass = ssl_result
                            self.ssl_filter_pass_output(tls_pass,tls_file)
                            #print 'cc1'
                        else:
                            tls_pass = ssl_result
                            self.ssl_filter_pass_output(tls_pass,tls_file)
                            #print 'cc2'
                    else:
                        if valid_algorithms[i+2] in ssl_result:#2
                            tls_pass = ssl_result
                            self.ssl_filter_pass_output(tls_pass,tls_file)
                            #print 'cc3'
                        else:
                            tls_fail = ssl_result
                            self.ssl_filter_fail_output(tls_fail,tls_file)
                            #print 'cc4'
            #for debug      
            #print ('pass item = %s' %tls_pass)
            #print ('fail item = %s' %tls_fail)

        else:
            print(colored("\n%s of Scan result is empty , Cancelled..." %tls_file,"yellow"))
        
    def ssl_result(self,tls_file):
        #Compare and output result
        global msg

        tls_find_fail = '/home/test/SecurityHole/%s_find_fail_filter*' %tls_file
        fileList = glob.glob(tls_find_fail)
        count_fail = len(fileList) # count the list
        
        fileRead = "".join(fileList) 
        print fileRead 
        if count_fail == 1: 
            with open('%s' %(fileRead), 'r' ) as f:
                read_file = f.read().split()
                msg = "<b>%s_Scan_Fail_Result</b> = " %tls_file + " , ".join(read_file)  
                print(colored("\nFailed the %s SSl/TLS Scan Testing" %tls_file,"red"))
        
        elif count_fail == 0:
            msg = "<b>%s_Scan_Pass_Result</b> = Pass" %tls_file
            print(colored("\nPassed the %s SSl/TLS Scan Testing" %tls_file,"yellow"))
        
        

    def runTest(self):
        global msg
        
        Security_Info = Security_Device()
        Security_Info.Connect_Device()
        Security_Info.Stop_HttpSimpleServer()
        Security_Info.Start_HttpSimpleServer()
                
        Common_info = Common()
        Common_info.Loading_DUT_IP()
        
        #Waiting time for DUT response
        n = 0
        while True:
            print(colored("\nWaiting for device response for %s" % response_time ,"yellow"))
            time.sleep(int(response_time))
            Common_info.PingDUT()
            if 'Pass' in ping_dut_result:
                break
            else:
                n += 1
                if n > 5:
                    pass
                
        
        if 'Pass' in ping_dut_result:
            #Starting Scanning
            Common_info.delete_file(delete_path='/home/test/SecurityHole/ssl*.txt')
            Common_info.delete_file(delete_path='/home/test/SecurityHole/tls*.txt')
            
            #self.ssl_scanner()         
            self.ssl_scanner2()
            self.getfile_tls()
                          
            self.getfile_ssl(ssl_file='ssl2')
            self.getfile_ssl(ssl_file='ssl3')

            self.ssl_filter_main(tls_file = "tls10")
            self.ssl_filter_main(tls_file = "tls11")
            self.ssl_filter_main(tls_file = "tls12")            
            self.ssl_filter_main(tls_file = "ssl2")
            self.ssl_filter_main(tls_file = "ssl3")
            
            self.ssl_result(tls_file = "tls10")
            tls10_msg = msg
            self.ssl_result(tls_file = "tls11")
            tls11_msg = msg
            self.ssl_result(tls_file = "tls12")
            tls12_msg = msg
            self.ssl_result(tls_file = "ssl2")
            ssl2_msg = msg
            self.ssl_result(tls_file = "ssl3")
            ssl3_msg = msg


            #Output Result to result.html
            if 'Pass' in tls10_msg and 'Pass' in tls11_msg and 'Pass' in tls12_msg  and 'Pass' in ssl2_msg and 'Pass' in ssl3_msg:
                self.result_message = tls10_msg + '<p>' + tls11_msg + '<p>' + tls12_msg + '<p>' + ssl2_msg + '<p>' + ssl3_msg  
            else:
                self.result_message = tls10_msg + '<p>' + tls11_msg + '<p>' + tls12_msg + '<p>' + ssl2_msg + '<p>' + ssl3_msg
                raise Exception (tls10_msg + tls11_msg + tls12_msg)
            
            Security_Info.Stop_HttpSimpleServer()
            Security_Info.Device_Logout()
        
        else:
            msg = ('Ping DUT ' + ping_dut_result + ' , Stop the Test')
            self.result_message = msg
            raise Exception (msg)
            

    def recover(self):
        board.sendcontrol(']')






