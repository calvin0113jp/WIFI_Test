# -*- coding: UTF-8 -*-

#-----For D-Link Dlab test Cases-----
# Install Setup
# 1.profile - boardfarm_config_example.json - dlink - mount docker file of /tftpboot/dba:/home
# 2.weblogin file - /tftpboot/dba/test_dba.py /tftpboot/dba/test_dba_nuclias.py



import re
import os
import sys
import subprocess
import rootfs_boot
import time
import json

from termcolor import *
from devices import board, wan, lan, wlan, prompt
from lib.common_ping import *
from lib.common_wifista import * # wifi module
from lib.common_ssh import * # import ssh module
from lib.common_docker import docker_command
from lib.common_tcpdump import tcpdump_command


#--------------General Setting--------------

# Docker path
webui_check_file = '/home/webui_check.txt'
webui_login_file = '/home/weblogin.txt'
device_info_file = '/home/device_info.txt'

# local path
local_webui_check_file = '/tftpboot/dba/webui_check.txt'
local_webui_login_file = '/tftpboot/dba/weblogin.txt'
local_device_info_file = '/tftpboot/dba/device_info.txt'

browser='chrome'

# dba config
dba_cli_file = '/home/test/boardfarm/tests/lib/dba_cli.json'
dba_cases = '/home/test/boardfarm/tests/lib/dba_cases.json'
nuclias_profile = '/tftpboot/dba/nuclias_profile.json'

# Nuclias cloud config

def Loading_nuclias_all(act):
    # load nuclias profile
        
    input_file = open (nuclias_profile)
    load_file = json.load(input_file)
    get_act = load_file[act]
    return get_act

nuclias_profile = Loading_nuclias_all(act='nuclias_common_xpath')

ssid_2g = nuclias_profile.get('p_ssid_name')
ssid_5g = ''
password_2g ='12345678'
password_5g = ''
user='admin'
pw='12345678'
dut_configured_ip = "192.168.0.120" # For test case


#-------------------------------------------


#------------Common Module------------------
class Command:
    ''' The module is used by dlink dlab web
    select_py
    0 = dlink_dlab_weblogin.py
    1 = test_dba_nuclias.py

    browser : chrome / firefox '''

    #-------------------------------------------------
    # Load config

    def Loading_DUT_IP(self):
        #load DUT IP

        global dut_account,dut_password,dut_model

        with open('/tftpboot/dba/device_info.txt', 'r') as f:
            line = f.readlines()
            dut_ip = str(line[0]).strip()
            dut_account = str(line[1]).strip()
            dut_password = str(line[2]).strip()
            dut_model = str(line[3]).strip()
        
        return dut_ip

    def Loading_cases(self,testplan,testcase):
        # load case form json
        # testplan = DKPxxxxx
        # testcase = 0001

        input_file = open (dba_cases)
        load_file = json.load(input_file)
        load_case = str(load_file[testplan]['title']) + str(load_file[testplan][testcase])

        return load_case
    
    def loading_cli_command(self,cli_main,cli_sub):
        # load cli command form json

        input_file = open (dba_cli_file)
        load_file = json.load(input_file)
        load_cli = str(load_file[cli_main][cli_sub])

        return load_cli

    #-------------------------------------------------
    # Web configured

    def Weblogin(self,case,select_py,browser):
        global web_result 

        with open("/tftpboot/dba/weblogin.txt","w") as f:
            f.write("%s\n" %case)
            f.write("%s\n" %browser)
 
        try:
            if select_py == 0:
                lan.sendline("\npytest -v -s --disable-warnings /home/test_dba.py::%s |tee %s" %(case,webui_check_file))

            elif select_py == 1: #nuclias
                lan.sendline("\npytest -v -s --disable-warnings /home/test_dba_nuclias.py::%s |tee %s" %(case,webui_check_file))

            i = lan.expect(['passed','Failed to login DUT','No such file or directory','Other error problem','no test','failed','AssertionError'], timeout=300000)
            if i == 0:
                web_result = 'Passed , GUI configured successfully'
            elif i == 1:
                web_result = 'Failed , Unable to weblogin , try 10 times'
            elif i == 2:
                web_result = 'Failed , Not found weblogin.py'
            elif i == 3:
                web_result = 'Failed , Other Error Problem , Sometimes DUT Not Found or Page Load Error'
            elif i == 4:
                web_result = 'Failed , Not found test items'
            elif i == 5 or i == 6:
                web_result = 'Failed , assert false item'
            
            lan.expect(prompt)
            print(colored("\n%s" %web_result,"yellow"))

        except:
            lan.expect(prompt)
            web_result = 'Failed , Unexpect issue' 
            print(colored("\n%s" %web_result,"red"))

    def delete_file(self,fileName):
        #Delete files before testing files

        print(colored("\nDeleting files if exist","yellow"))
        
        lan.sendline("rm -f %s" %fileName)
        lan.expect(prompt)

class Common_Result:
    ''' MOdule used by decide the result'''

    def check_ipaddress(self,ip_rule_list,ip_result):
        # ip_rule_list -> list
        # ip_result -> str
        # get_result -> list

        get_result = []
        for i in ip_rule_list:
            if i in ip_result:
                result = 'Passed - STA can get the corresponded IP<p>'
                get_result.append(result)
            else:
                result = 'Failed - STA cannot get the corresponded IP<p>'
        return get_result

class Web_Configured(rootfs_boot.RootFSBootTest):
    '''web configured'''
    
    def runTest(self,case,web_enable,select_py,browser,manual_ip,dut_ip,local_check):       
        # example        
        # case = web case
        # select_py = 0 -- check ping / select_py = 1 -- skip to check ping        
        # web_enable = configure the web or not        
        # manual_ip = 0 ,dut_ip = loading_dut_ip
        # manual_ip = 1, dut_ip = custom
        # local_check = 1 = local_webui_check_file
        # local_check = 0 = webui_check_file - wifi 

        webui_check_result = 'None' # default value
        ping_check = Ping()
        configure_web = Command()
        configure_web.delete_file(fileName=webui_check_file)

        if select_py == 0:
            print(colored("\nPing Check = 1" ,"yellow"))
            if manual_ip == 0:
                dut_info = configure_web.Loading_DUT_IP()    
                ping_result = ping_check.waiting_dut_bootup(dut_info)
            else:
                ping_result = ping_check.waiting_dut_bootup(dut_ip)

        elif select_py == 1:
            ping_result = 'Pass'
            print(colored("\nPing Check = 0" ,"yellow"))

        time.sleep(1)

        if 'Pass' in ping_result:
            print(colored("\nweb_enable = %s" %web_enable,"yellow"))
            if web_enable == 1:
                configure_web.Weblogin(case,select_py,browser)
                if 'Pass' in web_result:
                    if local_check == 1:
                        with open('%s' %(local_webui_check_file), 'r') as f: # read webui result
                            webui_check_result = f.read()
                    else:
                        lan.sendline('\ncat %s' %webui_check_file)
                        i = lan.expect(['pass'],timeout=10)
                        if i == 0:
                            webui_check_result = 'passed'
                        else:
                            webui_check_result = 'failed'
                    msg = 'Pass , Configure Web OK'                        
                else:
                    msg = 'Fail , Unable to Configure Web'
                    self.result_message = msg
                
                return msg , webui_check_result

            elif web_enable == 0:
                msg = 'None'
                return msg , webui_check_result
        else:
            msg = 'Unable to ping to DUT over 10 times'
            self.result_message = msg
            return msg , webui_check_result

    def recover(self):
        board.sendcontrol(']')

class Wlan_Sta(rootfs_boot.RootFSBootTest):
    '''Wifi connect without profile'''

    def runTest(self,dut_ip,dut_account,dut_password,case,browser,ssid,password,eap):

        # WIFI Sta

        common_wifista = wifista_command()
        common_wifista.connect_to_device()   

        common_wifista.write_dut_info_to_wifista(dut_ip,dut_account,dut_password,case,browser)
        status = common_wifista.wifi_main_process(ssid,password,eap)
                
        return status

    def recover(self):
        board.sendcontrol(']')

class Wlan_Sta_with_profile(rootfs_boot.RootFSBootTest):
    '''Wifi connect with profile'''

    def runTest(self,dut_ip,dut_account,dut_password,case,browser,ssid,password):

        # WIFI Sta

        common_wifista = wifista_command()
        common_wifista.connect_to_device()   

        common_wifista.write_dut_info_to_wifista(dut_ip,dut_account,dut_password,case,browser)
        status = common_wifista.wifi_main_process_with_profile(ssid,password)
                
        return status

    def recover(self):
        board.sendcontrol(']')

#------------Common Module------------------
    
# DBA_case_Nuclias_device_Automation_webUI
class Nuclias_device_webUI_Login_PC1_HTTP(rootfs_boot.RootFSBootTest):
    '''Check for the login - HTTP'''
    
    def runTest(self):
        configure_web = Command()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0001_1')
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                fail_result = '&emsp;Failed , PC1 is not able to login webgui and see DUT status'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                self.result_message = '&emsp;Passed , PC1 is able to login webgui and see DUT status without any problem'
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Login_PC1_HTTPS(rootfs_boot.RootFSBootTest):
    '''Check for the login - HTTPS'''
    
    def runTest(self):
        configure_web = Command()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0001_2')
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                fail_result = '&emsp;Failed , PC1 is not able to login webgui and see DUT status'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                self.result_message = '&emsp;Passed , PC1 is able to login webgui and see DUT status without any problem'
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Login_STA_HTTP(rootfs_boot.RootFSBootTest):
    '''Check for the login - HTTP'''
    
    def runTest(self):
        
        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0001_1')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        # Web Configured
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                fail_result = '&emsp;Failed , STA is not able to login webgui and see DUT status'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                self.result_message = '&emsp;Passed , STA is able to login webgui and see DUT status without any problem'
                 
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout() 
            
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Login_STA_HTTPS(rootfs_boot.RootFSBootTest):
    '''Check for the login - HTTPS'''
    
    def runTest(self):
        
        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0001_2')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        # Web Configured
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                fail_result = '&emsp;Failed , STA is not able to login webgui and see DUT status'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                self.result_message = '&emsp;Passed , STA is able to login webgui and see DUT status without any problem'
                 
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout() 
            
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_Logout_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the logout'''

    def runTest(self):
        
        configure_web = Command()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0002')
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                fail_result = '&emsp;Failed , PC1 is not able to logout to login page'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                self.result_message = '&emsp;Passed , PC1 is able to login page'
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_Logout_STA(rootfs_boot.RootFSBootTest):
    '''Check for the logout'''

    def runTest(self):
        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0002')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])
        
        # Web Configured
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                fail_result = '&emsp;Failed , STA is not able to logout to login page'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                self.result_message = '&emsp;Passed , STA is able to  to login page'
                 
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout() 
            
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_Language_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the Language'''

    def runTest(self):
        configure_web = Command()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0003')
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                fail_result = '&emsp;Failed - The webUI was not able to displayed by the Language'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                self.result_message = '&emsp;Passed - The webUI was able to displayed by the Language'
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_Language_STA(rootfs_boot.RootFSBootTest):
    '''Check for the Language'''

    def runTest(self):
        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0003')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        # Web Configured
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                fail_result = '&emsp;Failed - The webUI was not able to displayed by the Language'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                self.result_message = '&emsp;Passed - The webUI was able to displayed by the Language'
                 
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout() 
            
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_OverviewPage_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the OverviewPage'''

    def runTest(self):
        configure_web = Command()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0004')
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                fail_result = '&emsp;Failed - The info was not able to display correctly'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                self.result_message = '&emsp;Passed - The info was able to display correctly'
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_OverviewPage_STA(rootfs_boot.RootFSBootTest):
    '''Check for the OverviewPage'''

    def runTest(self):
        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0004')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])
        

        # Web Configured
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                fail_result = '&emsp;Failed - The info was not able to display correctly'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                self.result_message = '&emsp;Passed - The info was able to display correctly'
                 
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout() 
            
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_IPv6_setting_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the IPv6 setting'''

    def runTest(self):
        configure_web = Command()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0010')
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                fail_result = '&emsp;Failed - Default IPv6 Setting does not enabled'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                self.result_message = '&emsp;Passed - Default IPv6 Setting is enabled'
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_IPv6_setting_STA(rootfs_boot.RootFSBootTest):
    '''Check for the IPv6 setting'''

    def runTest(self):
        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0010')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        # Web Configured
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                fail_result = '&emsp;Failed - Default IPv6 Setting does not enabled'
                self.result_message = fail_result
                raise Exception (fail_result)
            else:
                common_wifista.wifi_connection_disconnect(ssid)
                common_wifista.device_logout()
                
                self.result_message = '&emsp;Passed - Default IPv6 Setting is enabled'
                 
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout() 
            
            msg = '&emsp;Unable to connect to DUT , No response from DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_IP_Connection_Type_Static_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the IP Connection Type to Static'''

    def runTest(self):
        
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_1')        
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure StaticIP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure StaticIP<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_3')  
        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip='192.168.0.120',local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip='192.168.0.120',user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check = ssh_device.get_cli_regular_result(cli="get management",regux="dhcp-status\W+(.*)",expect_value="Down")
                    ssh_device.device_logout()
                
                    if cli_check == True:
                        result_3 = '&emsp;3.Passed - Connection type display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - Connection type does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_IP_Connection_Type_DHCP_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the IP Connection Type to DHCP'''

    def runTest(self):
        # step1: configured IP
        # Step2: check IP in status
        # step3: check cli status
        
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_2')
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip='192.168.0.120',local_check=1)
        
        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure DHCP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure DHCP<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       
        
        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_4')
        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip=dut_ip,user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check = ssh_device.get_cli_regular_result(cli="get management",regux="dhcp-status\W+(.*)",expect_value="Up")
                    ssh_device.device_logout()
                
                    if cli_check == True:
                        result_3 = '&emsp;3.Passed - Connection type display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - Connection type does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = result_1 + result_2 + msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_IP_Connection_Type_Static_STA(rootfs_boot.RootFSBootTest):
    '''Check for the IP Connection Type to Static'''

    def runTest(self):

        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_1')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        configure_web = Command() 
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure StaticIP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure StaticIP<p>'
                self.result_message = result_1
        else:
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       
        
        
        #-------------------------------------------------------------------------------------------------------
        
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_3')
        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        dut_ip = '192.168.0.120'
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip='192.168.0.120',local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip="192.168.0.120",user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check = ssh_device.get_cli_regular_result(cli="get management",regux="dhcp-status\W+(.*)",expect_value="Down")
                    ssh_device.device_logout()
                
                    if cli_check == True:
                        result_3 = '&emsp;3.Passed - Connection type display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - Connection type does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_IP_Connection_Type_DHCP_STA(rootfs_boot.RootFSBootTest):
    '''Check for the IP Connection Type to DHCP'''

    def runTest(self):

        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_2')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        configure_web = Command() 
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip='192.168.0.120',local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure DHCP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure DHCP<p>'
                self.result_message = result_1
        else:
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       
        
        
        #-------------------------------------------------------------------------------------------------------
        
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0006_4')
        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)
        common_wifista.device_logout()
        
        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip=dut_ip,user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check = ssh_device.get_cli_regular_result(cli="get management",regux="dhcp-status\W+(.*)",expect_value="Down")
                    ssh_device.device_logout()
                
                    if cli_check == True:
                        result_3 = '&emsp;3.Passed - Connection type display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - Connection type does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_DNS_Name_servers_setting_DHCP_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the DNS Name servers setting with DHCP'''

    def runTest(self):

        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_1')        
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure DNS Name servers setting - DHCP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure DNS Name servers setting - DHCP<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_3')  
        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg1[0]:               
            if 'failed' in msg1[1]:
                result_2 = '&emsp;2.Failed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip=dut_ip,user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check1 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="8.8.8.8")
                    cli_check2 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="168.95.1.1")
                    ssh_device.device_logout()
                
                    if cli_check1 and cli_check2 == True:
                        result_3 = '&emsp;3.Passed - DNS Name servers display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - DNS Name servers does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_DNS_Name_servers_setting_Static_PC1(rootfs_boot.RootFSBootTest):
    '''Check for the DNS Name servers setting with Static'''

    def runTest(self):

        configure_web = Command()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_2')        
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure DNS Name servers setting - StaticIP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure DNS Name servers setting - StaticIP<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_4')  
        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip='192.168.0.120',local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip="192.168.0.120",user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check1 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="8.8.8.8")
                    cli_check2 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="168.95.1.1")
                    ssh_device.device_logout()
                
                    if cli_check1 and cli_check2 == True:
                        result_3 = '&emsp;3.Passed - DNS Name servers display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - DNS Name servers does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_DNS_Name_servers_setting_Static_STA(rootfs_boot.RootFSBootTest):
    '''Check for the DNS Name servers setting with Static'''

    def runTest(self):

        #----Loading config----
        configure_web = Command()
        configure_web.Loading_DUT_IP()
        dut_ip = dut_configured_ip
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_5')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        
        configure_web = Command() 
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip=dut_ip,local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure DNS Name servers setting - StaticIP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure DNS Name servers setting - StaticIP<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_4')
        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip=dut_ip,local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check StaticIP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip=dut_ip,user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check1 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="8.8.8.8")
                    cli_check2 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="168.95.1.1")
                    ssh_device.device_logout()
                
                    if cli_check1 and cli_check2 == True:
                        result_3 = '&emsp;3.Passed - DNS Name servers display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - DNS Name servers does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_device_webUI_DNS_Name_servers_setting_DHCP_STA(rootfs_boot.RootFSBootTest):
    '''Check for the DNS Name servers setting with DHCP'''

    def runTest(self):

        #----Loading config----
        configure_web = Command()
        configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_6')
        ssid = ssid_2g[0]
        password=password_2g
        dut_ip = dut_configured_ip
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        
        configure_web = Command()
         
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip=dut_ip,local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure DNS Name servers setting - DHCP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure DNS Name servers setting - DHCP<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0007_3')
        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)
        common_wifista.device_logout()
        
        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Status - Check DHCP<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip=dut_ip,user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check1 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="8.8.8.8")
                    cli_check2 = ssh_device.get_cli_regular_result(cli="get host dns",regux="dns\W+(.*\W+.*)",expect_value="168.95.1.1")
                    ssh_device.device_logout()
                
                    if cli_check1 and cli_check2 == True:
                        result_3 = '&emsp;3.Passed - DNS Name servers display correctly in CLI<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - DNS Name servers does not display correctly in CLI<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_NTP_Server_setting_PC1(rootfs_boot.RootFSBootTest):
    '''Check for NTP Server setting'''

    def runTest(self):

        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0009')        
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure NTP Server setting<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure NTP Server setting<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0009_1')  
        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - DUT can sync the time with the NTP server<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - DUT can sync the time with the NTP server<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip=dut_ip,user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check1 = ssh_device.get_cli_regular_result(cli="get ntp server",regux="server\W+(.*\W+.*\W+.*\W+.*)",expect_value="216.239.35.4")
                    cli_check2 = ssh_device.get_cli_regular_result(cli="get ntp server",regux="server\W+(.*\W+.*\W+.*\W+.*)",expect_value="ntp.dlink.com.tw")
                    cli_check3 = ssh_device.get_cli_regular_result(cli="get ntp server",regux="server\W+(.*\W+.*\W+.*\W+.*)",expect_value="ntp.nuclias.com")
                    ssh_device.device_logout()
                
                    if cli_check1 and cli_check2 and cli_check3 == True:
                        result_3 = '&emsp;3.Passed - CLI display correct NTP server information<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - CLI does not display NTP server information<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_NTP_Server_setting_STA(rootfs_boot.RootFSBootTest):
    '''Check for NTP Server setting'''

    def runTest(self):

        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0009')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])
         
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip=dut_ip,local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure NTP Server setting - DHCP<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure NTP Server setting - DHCP<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0009_1')
        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)
        common_wifista.device_logout()
        
        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - DUT can sync the time with the NTP server<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - DUT can sync the time with the NTP server<p>'
                self.result_message = result_1 + result_2

                # Check cli
                ssh_device = ssh_command()
                result_3 = ssh_device.main(ip=dut_ip,user=user,pw=pw)                
                if 'Unable' in result_3:
                    self.result_message = result_1 + result_2 + result_3
                    raise Exception (result_1 + result_2 + result_3)     
                else:    
                    cli_check1 = ssh_device.get_cli_regular_result(cli="get ntp server",regux="server\W+(.*\W+.*\W+.*\W+.*)",expect_value="216.239.35.4")
                    cli_check2 = ssh_device.get_cli_regular_result(cli="get ntp server",regux="server\W+(.*\W+.*\W+.*\W+.*)",expect_value="ntp.dlink.com.tw")
                    cli_check3 = ssh_device.get_cli_regular_result(cli="get ntp server",regux="server\W+(.*\W+.*\W+.*\W+.*)",expect_value="ntp.nuclias.com")
                    ssh_device.device_logout()
                
                    if cli_check1 and cli_check2 and cli_check3 == True:
                        result_3 = '&emsp;3.Passed - CLI display correct NTP server information<p>'          
                    else:
                        result_3 = '&emsp;3.Failed - CLI does not display correct NTP server information<p>'
                                
                    self.result_message = result_1 + result_2 + result_3
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Proxy_Setting_PC1(rootfs_boot.RootFSBootTest):
    '''Check for proxy setting'''

    def squid_proxy(self,dut_ip):
        # Step1: Starting to proxy server and tcpdump
        # Start proxy server
        # Start to capture packet
        
        docker_execute = docker_command()
        tcpdump_execute = tcpdump_command()
        docker_execute.connect_to_device()

        docker_pppoe_status = docker_execute.check_container(image='squid')
        
        if docker_pppoe_status == True:
           docker_execute.stop_container()
           docker_execute.start_container_proxy()
        else:
           docker_execute.start_container_proxy()
        
        tcpdump_execute.kill_tcpdump()
        tcpdump_execute.start_tcpdump(interface='eth1',filter='tcp port 3128 and host %s' %dut_ip,output_file='proxy.txt')
        docker_execute.device_logout()

    def Check_proxy_setting_cli(self,dut_ip):
        # Step3: Check proxy setting with cli
        
        ssh_device = ssh_command()
        result_2 = ssh_device.main(ip=dut_ip,user=user,pw=pw)
        if 'Unable' in result_2:
            result_2 = '&emsp;2.Failed - Unable to connect to DUT via SSH<p>'
        else:
            cli_check1 = ssh_device.get_cli_regular_result(cli="get management proxy-enable",regux="Value\W+proxy-enable\W+(\w+)",expect_value="Up")
            cli_check2 = ssh_device.get_cli_regular_result(cli="get management proxy-host",regux="Value\W+proxy-host\W+(.*)",expect_value="192.168.0.80")
            cli_check3 = ssh_device.get_cli_regular_result(cli="get management proxy-port",regux="Value\W+proxy-port\W+(.*)",expect_value="3128")
            
            if cli_check1 and cli_check2 and cli_check3 == True:
                result_2 = '&emsp;2.Passed - CLI display correct Proxy setting<p>'          
            else:
                result_2 = '&emsp;2.Failed - CLI does not display display correct Proxy setting<p>'
        
        return result_2

    def Reboot_DUT_cli(self,dut_ip):
        # Step4: Reboot DUT with cli

        print(colored("\nReboot the DUT , Please wait for 120 sec","yellow"))
        lan.sendline("\n\n\n")
        lan.expect(prompt,timeout=10)
        lan.sendline("reboot")
        lan.expect("closed")
        lan.expect(prompt,timeout=30)
        time.sleep(120)

        ping_check = Ping()
        ping_result = ping_check.waiting_dut_bootup(dut_ip)
        if 'Pass' in ping_result:
            result_3 = '&emsp;3.Passed - Ping to DUT OK'
        else:
            result_3 = '&emsp;3.Failed - Unable to Ping to DUT , maybe hang up<p>'

        return result_3

    def Check_packet(self,dut_ip):
        # Step5: Check packet that contain the proxy service

        docker_execute = docker_command()
        tcpdump_execute = tcpdump_command()
        docker_execute.connect_to_device()
        tcpdump_execute.kill_tcpdump()

        try:
            lan.sendline('\ncat proxy.txt |grep %s' %dut_ip)
            i = lan.expect(['%s' %dut_ip],timeout=10)
            if i == 0:
                result_4 = '&emsp;4.Passed , Capture packet - Found host server ip address<p>'
                print(colored("\nPassed , Capture packet - Found host server ip address","yellow"))
        except:
            result_4 = '&emsp;4.Failed , Capture packet - Does not found host ip address<p>'
            print(colored("\nFailed , Capture packet - Does not found host ip address","yellow"))

        #docker_execute.stop_container()
        docker_execute.device_logout()

        return result_4

    def runTest(self):
        
        # Step1: Starting to proxy server and tcpdump
        # Step2: Enable proxy server
        # Step3: Check proxy setting with cli
        # Step4: Reboot DUT with cli
        # Step5: Check packet that contain the proxy service

        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        #----------------------

        # Step1
        self.squid_proxy(dut_ip)
        
        #-------------------------------------------------------------------------------------------------------
        
        #Step2
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0012')        
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure Proxy setting<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure Proxy setting<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------
        
        # Step3
        result_2 = self.Check_proxy_setting_cli(dut_ip)
        if 'Unable' in result_2:
            self.result_message = result_1 + result_2
            raise Exception (result_1 + result_2)
        else:
            self.result_message = result_1 + result_2
        #-------------------------------------------------------------------------------------------------------
        
        # Step4
        result_3 = self.Reboot_DUT_cli(dut_ip)
        if 'Unable' in result_3:
            self.result_message = result_1 + result_2 + result_3
            raise Exception (result_1 + result_2 + result_3)
        else:
            self.result_message = result_1 + result_2 + result_3
        #-------------------------------------------------------------------------------------------------------
        
        # Step5       
        result_4 = self.Check_packet(dut_ip)
        if 'Failed' in result_4:
            self.result_message = result_1 + result_2 + result_3 + result_4
            raise Exception (result_1 + result_2 + result_3 + result_4)
        else:
            self.result_message = result_1 + result_2 + result_4

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Proxy_Setting_STA(rootfs_boot.RootFSBootTest):
    '''Check for proxy setting'''

    def runTest(self):
        
        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0012')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])
         
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=1,dut_ip=dut_ip,local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Configure Proxy setting<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Configure Proxy setting<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)     

        start_proxy_test = Nuclias_device_webUI_Proxy_Setting_PC1(None)
        
        #-------------------------------------------------------------------------------------------------------
        
        # Step3
        result_2 = start_proxy_test.Check_proxy_setting_cli(dut_ip)
        if 'Unable' in result_2:
            self.result_message = result_1 + result_2
            raise Exception (result_1 + result_2)
        else:
            self.result_message = result_1 + result_2
        #-------------------------------------------------------------------------------------------------------
        
        # Step4
        result_3 = start_proxy_test.Reboot_DUT_cli(dut_ip)
        if 'Unable' in result_3:
            self.result_message = result_1 + result_2 + result_3
            raise Exception (result_1 + result_2 + result_3)
        else:
            self.result_message = result_1 + result_2 + result_3
        #-------------------------------------------------------------------------------------------------------
        
        # Step5       
        result_4 = start_proxy_test.Check_packet(dut_ip)
        if 'Failed' in result_4:
            self.result_message = result_1 + result_2 + result_3 + result_4
            raise Exception (result_1 + result_2 + result_3 + result_4)
        else:
            self.result_message = result_1 + result_2 + result_4

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Firmware_Upgrade_PC1(rootfs_boot.RootFSBootTest):
    '''Check for firmware upgrade'''

    def runTest(self):

        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0011_1')        
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Firmware cannot be upgraded<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Firmware can be upgraded successful<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0011_2')  
        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Firmware version does not disaply correctly in local setting and status<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Firmware version disaply correctly in local setting and status<p>'
                self.result_message = result_1 + result_2                
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Firmware_Upgrade_fake_image_PC1(rootfs_boot.RootFSBootTest):
    '''Check for fake firmware upgrade'''

    def runTest(self):

        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0011_3')        
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Warning page does not display correctly'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Warning page display correctly'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Firmware_Upgrade_STA(rootfs_boot.RootFSBootTest):
    '''Check for firmware upgrade'''

    def runTest(self):

        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0011_1')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])
     
        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Firmware cannot be upgraded<p>'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Firmware can be upgraded successful<p>'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

        #-------------------------------------------------------------------------------------------------------

        case = configure_web.Loading_cases(testplan='testplan1',testcase='0011_2')  
        
        # WIFI Sta
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])
                
        msg1 = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=0)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:               
            if 'failed' in msg[1]:
                result_2 = '&emsp;2.Failed - Firmware version does not disaply correctly in local setting and status<p>'
                self.result_message = result_1 + result_2
                raise Exception (result_1 + result_2)
            else:
                result_2 = '&emsp;2.Passed - Firmware version disaply correctly in local setting and status<p>'
                self.result_message = result_1 + result_2                
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(2)'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Firmware_Upgrade_fake_image_STA(rootfs_boot.RootFSBootTest):
    '''Check for fake firmware upgrade'''

    def runTest(self):

        #----Loading config----
        configure_web = Command()
        dut_ip = configure_web.Loading_DUT_IP()
        case = configure_web.Loading_cases(testplan='testplan1',testcase='0011_3')
        ssid = ssid_2g[0]
        password=password_2g
        eap = 0
        #----------------------

        # WIFI Sta
        common_wifista = wifista_command()
        Wlan = Wlan_Sta(None)
        connected_status = Wlan.runTest(dut_ip,dut_account,dut_password,case,browser,ssid,password,eap)
        
        if 'Fail' not in connected_status[0]:
            print(colored("\nWifi Connected Passed , Next Steps","yellow"))
            self.result_message = connected_status[0]
        else:
            common_wifista.wifi_connection_disconnect(ssid)
            common_wifista.device_logout()
            self.result_message = connected_status[0]
            raise Exception (connected_status[0])

        web = Web_Configured(None)
        msg = web.runTest(case,web_enable=1,select_py=0,browser='chrome',manual_ip=0,dut_ip=None,local_check=1)
        common_wifista.device_logout()

        if 'Unable' not in msg[0]:              
            if 'failed' in msg[1]:
                result_1 = '&emsp;1.Failed - Warning page does not display correctly'
                self.result_message = result_1
                raise Exception (result_1)
            else:
                result_1 = '&emsp;1.Passed - Warning page display correctly'
                self.result_message = result_1
        else: 
            msg = '&emsp;Unable to connect to DUT , No response from DUT(1)'
            self.result_message = msg
            raise Exception (msg)       

    def recover(self):
        board.sendcontrol(']')

class Nuclias_device_webUI_Vlan_function_PC1(rootfs_boot.RootFSBootTest):
    '''Check for Vlan function'''

    def runTest(self):

        self.result_message = "&emsp;Not yet automation"
        print(colored("Not yet automation","yellow"))

    def recover(self):
        board.sendcontrol(']')


#-------------------------------------------------------------------------------------------------------