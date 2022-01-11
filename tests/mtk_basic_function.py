# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
# coding = utf-8


# History
# 2019/2/21-2/22 Add PowerTable2g & PowerTable5g
# 2019/2/26 Add Single SKU
# 2019/2/26 Add Product information
# 2019/3/4 Add Product_information_fwupgrade
# 2019/3/5 1.Add Product_information_default
#          2.Firmware - Firmware upgrade & Firmware downgrade
# 2019/3/6 Add channel_list and modify the chklst() - add the ch_list - wlan0_ch, wlan1_ch
# 2019/3/13 Add Firmware version check 
# 2019/3/15 Firmware version check

#           1.WebUI version check
#           2.Hidden page version check
#           3.Release note check
# 2019/3/18 4.Add MD5Checksum and firmware date
#           *Modify SingleSKU_MD5
# 2019/3/19 5.Add Default_value_WifiPSK
#           6.Add Default_value_LANIP            
#           Add when item is runs failed , how to goes to failed states and then output
#           7.Add Default_value_WANtype
#           Add Firmware_verCheck_Binfile
#           Modify the fwupgrade to new.bin and old.bin / and add the script to copy the file
# 2019/4/18 1.Add board.login_elecom() #Detect console if support authentication
#           2.Modify chklst() download to local file 

# 2019/8/27 1.Modify upgrade / downgrade regular of version build from (.\w.*)(.*)
#           2.Modify Product_information_fwupgrade of uci command from \D.* to \d.*
#           3.Modify Firmware_verCheck_WEBUI of uci command from \D.* to \d.*
#           4.Modify Firmware_verCheck_hiddenPage to (.*)
#           5.Modify Firmware_verCheck_MD5CheckSum of fw_date
#           6.Modify Default_value_LANIP of regular ipaddress
# 2019/8/28 1.Modify firstboot in Product_information_default
#           2.Modify Default_value_WANtype of uci get
#           3.Modify Firmware_verCheck_MD5CheckSum of fw_date
#           4.Modify Firmware_verCheck_WEBUI of fw_ver
# 2019/8/30 1.Modify Channel_list to add the new 5G spec
#           2.Modify uci command to support is the key is empty
#           3.Modify Firmware_verCheck_WEBUI to support the dynamic admin password
# 2019/9/2  Add board.login_elecom() in every test items
# 2019/11/1 Remove wget in Firmware_verCheck_WEBUI (Due to wget sometimes failed from download server)
#           Add wget command in Docker container images (Add Dockerfile in bft-node)


import re
import os
import sys
import subprocess
import rootfs_boot
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from lib import installers
from termcolor import *

       

class PowerTable2g(rootfs_boot.RootFSBootTest):
    '''Power table related setting 2G (MTK).'''
    def runTest(self):
        board.login_elecom()
        board.sendline('rm -f /tmp/powertable.txt')
        board.expect(prompt)
        board.sendline('find /etc/Wireless/RT2860/ -name "RT2860.dat" > /tmp/powertable.txt')
        board.expect(prompt)
        board.check_output('cat /tmp/powertable.txt')
        powertable_search = board.before     
        print powertable_search

        if 'RT2860.dat' in powertable_search:
            print 'For NONE-DBDC ,2533/1900/1750'

            # For MTK (non-DBDC ,2533/1900/1750)
            # 2.4G
            board.sendline('cat /etc/Wireless/RT2860/RT2860.dat |grep "SKUenable\|BFBACKOFFenable"')
            sku = board.expect(['SKUenable=1','SKUenable=0'],timeout=10)
            bf = board.expect(['BFBACKOFFenable=1','BFBACKOFFenable=0'],timeout=10)
            
            if sku == 0 and bf == 0:
                print '11'
                print(colored("\nPass - SKU=1 & BFBACKOFF=1","yellow"))
                self.result_message = 'Pass - SKU=1 & BFBACKOFF=1'

            elif sku == 0 and bf == 1:
                print '10'
                print(colored("\nSKU=1 & BFBACKOFF=0","red"))
                msg = 'SKU=1 & BFBACKOFF=0'
                self.result_message = msg
                raise Exception (msg)

            elif sku == 1 and bf == 0:
                print '01'
                print(colored("\nSKU=0 & BFBACKOFF=1","red"))
                msg = 'SKU=0 & BFBACKOFF=1'
                self.result_message = msg
                raise Exception (msg)

            else:
                print '00'
                print(colored("\nSKU=0 & BFBACKOFF=0","red"))
                msg = 'SKU=0 & BFBACKOFF=0'        
                self.result_message = msg
                raise Exception (msg)

        else:
            print 'For DBDC 1167'

            # For DBDC 1167
            # 2.4G
            board.sendline('cat /etc/Wireless/RT2860/RT2860_2G.dat |grep "SKUenable\|BFBACKOFFenable"')
            sku = board.expect(['SKUenable=1','SKUenable=0'],timeout=10)
            bf = board.expect(['BFBACKOFFenable=1','BFBACKOFFenable=0'],timeout=10)
            
            if sku == 0 and bf == 0:
                print '11'
                print(colored("\nPass - SKU=1 & BFBACKOFF=1","yellow"))
                self.result_message = 'Pass - SKU=1 & BFBACKOFF=1'

            elif sku == 0 and bf == 1:
                print '10'
                print(colored("\nSKU=1 & BFBACKOFF=0","red"))
                msg = 'SKU=1 & BFBACKOFF=0'
                self.result_message = msg
                raise Exception (msg)

            elif sku == 1 and bf == 0:
                print '01'
                print(colored("\nSKU=0 & BFBACKOFF=1","red"))
                msg = 'SKU=0 & BFBACKOFF=1'
                self.result_message = msg
                raise Exception (msg)

            else:
                print '00'
                print(colored("\nSKU=0 & BFBACKOFF=0","red"))
                msg = 'SKU=0 & BFBACKOFF=0'
                self.result_message = msg
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class PowerTable5g(rootfs_boot.RootFSBootTest):
    '''Power table related setting 5G (MTK).'''
    def runTest(self):
        board.login_elecom()
        board.sendline('rm -f /tmp/powertable.txt')
        board.expect(prompt)
        board.sendline('find /etc/Wireless/iNIC/ -name "iNIC_ap.dat" > /tmp/powertable.txt')
        board.expect(prompt)
        board.check_output('cat /tmp/powertable.txt')
        powertable_search = board.before     
        print powertable_search

        if 'iNIC_ap.dat' in powertable_search:
            print 'For NONE-DBDC ,2533/1900/1750'

            # For MTK (non-DBDC ,2533/1900/1750)
            # 5G
            board.sendline('cat /etc/Wireless/iNIC/iNIC_ap.dat |grep "SKUenable\|BFBACKOFFenable"')
            sku = board.expect(['SKUenable=1','SKUenable=0'],timeout=10)
            bf = board.expect(['BFBACKOFFenable=1','BFBACKOFFenable=0'],timeout=10)
            
            if sku == 0 and bf == 0:
                print '11'
                print(colored("\nPass - SKU=1 & BFBACKOFF=1","yellow"))
                self.result_message = 'Pass - SKU=1 & BFBACKOFF=1'

            elif sku == 0 and bf == 1:
                print '10'
                print(colored("\nSKU=1 & BFBACKOFF=0","red"))
                msg = 'SKU=1 & BFBACKOFF=0'
                self.result_message = msg
                raise Exception (msg)

            elif sku == 1 and bf == 0:
                print '01'
                print(colored("\nSKU=0 & BFBACKOFF=1","red"))
                msg = 'SKU=0 & BFBACKOFF=1'
                self.result_message = msg
                raise Exception (msg)

            else:
                print '00'
                print(colored("\nSKU=0 & BFBACKOFF=0","red"))
                msg = 'SKU=0 & BFBACKOFF=0'
                self.result_message = msg
                raise Exception (msg)
           
        else:
            print 'For DBDC 1167'

            # For DBDC 1167
            # 5G
            board.sendline('cat /etc/Wireless/RT2860/RT2860_5G.dat |grep "SKUenable\|BFBACKOFFenable"')
            sku = board.expect(['SKUenable=1','SKUenable=0'],timeout=10)
            bf = board.expect(['BFBACKOFFenable=1','BFBACKOFFenable=0'],timeout=10)
            
            if sku == 0 and bf == 0:
                print '11'
                print(colored("\nPass - SKU=1 & BFBACKOFF=1","yellow"))
                self.result_message = 'PASS - SKU=1 & BFBACKOFF=1'

            elif sku == 0 and bf == 1:
                print '10'
                print(colored("\nSKU=1 & BFBACKOFF=0","red"))
                msg = 'SKU=1 & BFBACKOFF=0'
                self.result_message = msg
                raise Exception (msg)

            elif sku == 1 and bf == 0:
                print '01'
                print(colored("\nSKU=0 & BFBACKOFF=1","red"))
                msg = 'SKU=0 & BFBACKOFF=1'
                self.result_message = msg
                raise Exception (msg)

            else:
                print '00'
                print(colored("\nSKU=0 & BFBACKOFF=0","red"))
                msg  = 'SKU=0 & BFBACKOFF=0'
                self.result_message = msg
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

    

       
        
class Product_information_fwupgrade(rootfs_boot.RootFSBootTest):
    '''Check Product information after Firmware Upgrade. (MTK)'''

    def chklst(self):
        #Download the chklst.txt from DUT
        os.system('rm -f /home/chklst.txt')
        time.sleep(3)        
        process = pexpect.spawn('wget --http-user=ETAbBPxg54yV7cHYpKyMMaTIyXkMU6Xe --http-password=pTRYlWTe09y3ZhzW1myZ14jMNVitadQP -P /home/ http://192.168.2.1:12250/chklst.txt')
        process.logfile_read = sys.stdout
        process.expect('Saving to:')

        #installers.install_wget(lan)
        #lan.sendline('wget --http-user=ETAbBPxg54yV7cHYpKyMMaTIyXkMU6Xe --http-password=pTRYlWTe09y3ZhzW1myZ14jMNVitadQP -P /home/ http://192.168.2.1:12250/chklst.txt')
        #lan.expect('chklst.txt',timeout=15)
        #lan.expect('Saving to:')
        #lan.expect(prompt)
        #lan.check_output('cat /home/chklst.txt')
 
        #Get board information from chklst.txt
        global wlan0_mac, wlan1_mac, lan_mac, wan_mac, ssid, ssid_1, domain, firmware_version, checksum
        f = open('/home/chklst.txt','r')
        chklst =''
        chklst = f.read()
        chklst = chklst.replace('<br>','') #remove <br> to the correct format
        wlan0_mac = re.findall('WLAN MAC 0: \w.*',chklst)
        wlan1_mac = re.findall('WLAN MAC 1: \w.*',chklst)
        lan_mac = re.findall('LAN MAC: \w.*',chklst)
        wan_mac = re.findall('WAN MAC: \w.*',chklst)
        ssid = re.findall('SSID: \w.*',chklst)
        ssid_1 = re.findall('SSID_1: \w.*',chklst)
        domain = re.findall('Wireless Domain: \d.*',chklst)
        firmware_version = str(re.findall('Firmware Version: ver\d.*',chklst))
        checksum = re.findall('checksum: (\w.*)',chklst)
        checksum = "".join(checksum) # list to str
        
        #For Channel List
        global wlan0_ch, wlan1_ch
        wlan0_ch = re.findall('WLAN 0 Channel List: (\d.*)',chklst)
        wlan1_ch = re.findall('WLAN 1 Channel List: (\d.*)',chklst)
        wlan0_ch = str(wlan0_ch)
        wlan1_ch = str(wlan1_ch)

    def uci_command(self):        
        global model_name, wpa_2g_password, wpa_5g_password , wps_pin
        #Get board information from uci command
        #model name
        board.login_elecom() #Detect console if support authentication 
        
        n=0
        o=0
        p=0
        q=0
        
        while True:
            try:
                board.sendline('uci show |grep cameo.cameo.model_name')
                board.expect('cameo.cameo.model_name=(\D.+)')
                model_name = board.match.group(1)
                model_name = model_name.replace('\'','')
                time.sleep(1)
                if model_name.strip() =='':
                    print(colored("\nmodel_name is empty , Retry for %s" %n,"yellow"))
                    n = n + 1
                    if n > 3:
                        break
                else:
                    print(colored("\nmodel_name found","yellow"))
                    break
            except:
                print(colored("\nError command , Will Retry","red"))
        
        #wpa_2g_password
        while True:
            try:
                board.sendline('uci show |grep qcawifi_router.wlan0.vap0_psk_pass_phrase')
                board.expect('qcawifi_router.wlan0.vap0_psk_pass_phrase=(\D.+)')
                wpa_2g_password = board.match.group(1)
                wpa_2g_password = wpa_2g_password.replace('\'','')
                time.sleep(1)
                if wpa_2g_password.strip() =='':
                    print(colored("\nwpa_2g_password is empty , Retry for %s" %o,"yellow"))
                    o = o + 1
                    if o > 3:
                        break
                else:
                    print(colored("\nwpa_2g_password found","yellow"))
                    break
            except:
                print(colored("\nError command , Will Retry","red"))
        
        #wpa_5g_password
        while True:
            try:
                board.sendline('uci show |grep qcawifi_router.wlan1.vap0_psk_pass_phrase')
                board.expect('qcawifi_router.wlan1.vap0_psk_pass_phrase=(\D.+)')
                wpa_5g_password = board.match.group(1)
                wpa_5g_password= wpa_5g_password.replace('\'','')
                time.sleep(1)
                if wpa_5g_password.strip() =='':
                    print(colored("\nwpa_5g_password is empty , Retry for %s" %p,"yellow"))
                    p = p + 1
                    if p > 3:
                        break
                else:
                    print(colored("\nwpa_5g_password found","yellow"))
                    break
            except:
                print(colored("\nError command , Will Retry","red"))
        
        #wps_pin
        #GUI only get the wlan0 s wps pin_value
        while True:
            try:
                board.check_output('uci get qcawifi_router.wlan0.wps_pin')
                wps_pin = re.findall(r'\d{8}',board.before)
                wps_pin = "".join(wps_pin).strip() # list to str / remove space
                time.sleep(1)
                if wps_pin.strip() =='':
                    print(colored("\nwps_pin is empty , Retry for %s" %q,"yellow"))
                    q = q + 1
                    if q > 3:
                        break
                else:
                    print(colored("\nwps_pin found","yellow"))
                    break         
            except:
                print(colored("\nError command , Will Retry","red"))
    
    def fw_upgrade(self):        
        #Put the fw file into "/tftpboot/ for the example"
	dir = "/tftpboot/upgrade/"
	for root, dirs, files in os.walk(dir):
    		for file in files:
			find_model = os.path.join(root,file)
	
	model = find_model.replace('/tftpboot/upgrade/','')
	fw_name = model
	fw_path = '/tftpboot/upgrade/'
	tftp_server_ip = '192.168.2.50' # lan pc
	hwid_remove_version = (model[-10:])
	hwid_add = model.replace(hwid_remove_version,'')
	hwid = 'MT7621_ELECOM_'+ hwid_add
	header_length = 32
	md5 = 32
	hwid_lens = len(hwid) 
		

	file_size = os.stat(fw_path+fw_name)
	size_source = (file_size.st_size)
	print ("Firmware source size=%s" %(size_source))
	size_result = (size_source - header_length - md5 - hwid_lens)
	print ("Now will upgrading to DUT's size=%s" %(size_result))

        # This test can damage flash, so to properly recover we need
        # to reflash upon recovery
        self.reflash = True

        board.login_elecom() #Detect console if support authentication        
        board.sendline("cd /tmp")
	board.sendline("tftp -g -r new.bin %s" %(tftp_server_ip))
	board.expect(prompt)
	board.sendline("/sbin/sysupgrade_md5.sh %s /tmp/new.bin" %(size_result))
	board.expect(prompt)
        time.sleep(5)
	board.sendline("sysupgrade_new -c /tmp/img_splitaa")
        board.expect("Restarting system", timeout=350)

        #lib.common.wait_for_boot(board)
        #board.boot_linux()
        board.wait_for_linux()


    def runTest(self):
        #Store the value before fw_upgrade
        self.chklst()
        self.uci_command()
        wlan0_mac_b = wlan0_mac
        wlan1_mac_b = wlan1_mac
        lan_mac_b = lan_mac
        wan_mac_b = wan_mac
        ssid_b = ssid
        ssid_1_b = ssid_1
        domain_b = domain
        model_name_b = model_name
        wpa_2g_password_b = wpa_2g_password
        wpa_5g_password_b = wpa_5g_password
        wps_pin_b = wps_pin

        #Upgrade and compare value between before and after
        self.fw_upgrade()
        self.chklst()
        self.uci_command()
        if wlan0_mac_b == wlan0_mac and wlan1_mac_b == wlan1_mac and lan_mac_b == lan_mac and wan_mac_b == wan_mac and ssid_b == ssid and ssid_1_b == ssid_1 and domain_b == domain and model_name_b == model_name and wpa_2g_password_b == wpa_2g_password and wpa_5g_password_b == wpa_5g_password and wps_pin_b == wps_pin:
            pass
        else:
            msg = 'Failed ,The result is not the same as before value'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Product_information_default(rootfs_boot.RootFSBootTest):
    '''Check Product information after Reset to default. (MTK)'''

    def runTest(self):
        #Store the value before reset to default
        product = Product_information_fwupgrade(None)
        product.chklst()
        product.uci_command()
        wlan0_mac_b = wlan0_mac
        wlan1_mac_b = wlan1_mac
        lan_mac_b = lan_mac
        wan_mac_b = wan_mac
        ssid_b = ssid
        ssid_1_b = ssid_1
        domain_b = domain
        model_name_b = model_name
        wpa_2g_password_b = wpa_2g_password
        wpa_5g_password_b = wpa_5g_password
        wps_pin_b = wps_pin

        #DUT reset to default      
        print(colored("\nDUT will staring to default, please wait!","yellow"))
        try:
            board.sendline('firstboot')
            i = board.expect(['Reset default process is finished','Erase char'],timeout=15)
            if i == 0:
                #For new behavior eq.GST2
                board.expect(prompt)
                print(colored("\nDetect new behavior for reset","yellow"))
            if i == 1:
                #For old behavior eq.GST1
                board.expect(prompt)            
                print(colored("\nDetect old behavior for reset","yellow"))
        except:
            print(colored("\nUnexcept firstboot","red"))
        
        board.sendline('reboot')
        board.expect('Restarting system',timeout=15)
        board.wait_for_linux()
        
        #Compare value between before and after
        product.chklst()
        product.uci_command()
        if wlan0_mac_b == wlan0_mac and wlan1_mac_b == wlan1_mac and lan_mac_b == lan_mac and wan_mac_b == wan_mac and ssid_b == ssid and ssid_1_b == ssid_1 and domain_b == domain and model_name_b == model_name and wpa_2g_password_b == wpa_2g_password and wpa_5g_password_b == wpa_5g_password and wps_pin_b == wps_pin:
            pass
        else:
            msg = "Failed ,The result is not the same as before value"
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Firmware_upgrade(rootfs_boot.RootFSBootTest):
    '''Testing FW can be upgraded from last formal release version(MTK).'''
    def runTest(self):
        product = Product_information_fwupgrade(None)
        product.fw_upgrade() 
        board.sendline('uci show|grep cameo.system.fw_version_build')
        #board.expect('cameo.system.fw_version_build=(.\w.*)')
        board.expect('cameo.system.fw_version_build=(.*)')
        fw_version = board.match.group(1)
        fw_version = fw_version.replace('\'','')
        fw_version = fw_version.replace('cameo.system.fw_version_build_rc=rc1','')
        
        print(colored("\nUpgrade FW version is %s" % fw_version,"yellow"))
        self.result_message = 'FW version is %s' %(fw_version)

class Firmware_downgrade(rootfs_boot.RootFSBootTest):
    '''Testing FW can be downgraded from last formal release version(MTK).'''

    def fw_downgrade(self):        
        #Put the fw file into "/tftpboot/ for the example"
	dir = "/tftpboot/downgrade/"
	for root, dirs, files in os.walk(dir):
    		for file in files:
			find_model = os.path.join(root,file)
	
	model = find_model.replace('/tftpboot/downgrade/','')
	fw_name = model
	fw_path = '/tftpboot/downgrade/'
	tftp_server_ip = '192.168.2.50' # lan pc
	hwid_remove_version = (model[-10:])
	hwid_add = model.replace(hwid_remove_version,'')
	hwid = 'MT7621_ELECOM_'+ hwid_add
	header_length = 32
	md5 = 32
	hwid_lens = len(hwid) 
		

	file_size = os.stat(fw_path+fw_name)
	size_source = (file_size.st_size)
	print ("Firmware source size=%s" %(size_source))
	size_result = (size_source - header_length - md5 - hwid_lens)
	print ("Now will upgrading to DUT's size=%s" %(size_result))

        # This test can damage flash, so to properly recover we need
        # to reflash upon recovery
        self.reflash = True

        
        board.login_elecom() #Detect console if support authentication
        board.sendline("cd /tmp")
        board.sendline("tftp -g -r old.bin %s" %(tftp_server_ip))
	board.expect(prompt)
	board.sendline("/sbin/sysupgrade_md5.sh %s /tmp/old.bin" %(size_result))
        time.sleep(5)
	board.expect(prompt)
	board.sendline("sysupgrade_new -c /tmp/img_splitaa")
        board.expect("Restarting system", timeout=350)

        #lib.common.wait_for_boot(board)
        #board.boot_linux()
        board.wait_for_linux()

    def runTest(self):
        self.fw_downgrade() 
        board.sendline('uci show|grep cameo.system.fw_version_build')
        #board.expect('cameo.system.fw_version_build=(.\w.*)')
        board.expect('cameo.system.fw_version_build=(.*)')
        fw_version = board.match.group(1)
        fw_version = fw_version.replace('\'','')
        fw_version = fw_version.replace('cameo.system.fw_version_build_rc=rc1','')
        
        print(colored("\nDowngrade FW version is %s" % fw_version,"yellow"))
        self.result_message = 'FW version is %s' %(fw_version)


class Firmware_verCheck_releasenote(rootfs_boot.RootFSBootTest):
    '''File name and Checksum must match release note (MTK).'''

    def find_filename(self):
        global fw_file, fw_file_name, releasenote
        #find fw filename
        fw_filename_path = "/tftpboot/upgrade/"
	for root, dirs, files in os.walk(fw_filename_path):
    		for file in files:
			fw_file = os.path.join(root,file) 
        fw_file_name = fw_file.replace(fw_filename_path,'')

        #find releasenote file
        
        releasenote_path = "/tftpboot/releasenote/"
	for root, dirs, files in os.walk(releasenote_path):
    		for file in files:
			releasenote_file = os.path.join(root,file)                
        releasenote = []
        f = open(releasenote_file,'r')
        for line in f.readlines()[0:50]:#read 50 lines
            line = line.strip()
            str(releasenote.append(str(line)))
        f.close()
        releasenote = "".join(releasenote)# list to str


    def runTest(self):
        self.find_filename()
        #get chklst value
        product = Product_information_fwupgrade(None)
        product.chklst()
        
        if checksum in releasenote:
            if fw_file_name in releasenote:
                print '\nchecksum - Passed!'
                print '\nfw_file_name - Passed!'
            else:
                print '\nchecksum - Passed!'
                print '\nfw_file_name - Failed!'
                msg = "fw_file_name is not correctly"
                self.result_message = msg + ',The result is %s' %(fw_file_name)
                raise Exception (msg)

        else:
            if fw_file_name in releasenote:
                print '\nchecksum - Failed'
                print '\nfw_file_name - Passed'
                msg = "checksum is not correctly"
                self.result_message = msg + ',The result is %s' %(checksum)
                raise Exception (msg)

            else:
                print '\nchecksum & fw_file_name - Failed'
                msg = "checksum and fw_file_name are not correctly"
                self.result_message = msg + ',The result is %s , %s' %(checksum, fw_file_name)
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')



class Firmware_verCheck_WEBUI(rootfs_boot.RootFSBootTest):
    '''Version /build number must be correct in WebUI (MTK).'''

    def uci_getVer(self):
        global uci_fw_ver
        #Get the information from uci and find the version from firmware.html
        board.login_elecom()
        board.sendline('\n\n\n')
        board.expect(prompt)
        board.sendline('uci show cameo.system.fw_version\n')
        i = board.expect(["=(\d{1,1}.\d{1,3})","'(\d{1,1}.\d{1,3})'"],timeout=15)
        if i == 0:
            print(colored("\nuci fw_verion=old","yellow"))
            uci_fw_ver = board.match.group(1)
        if i == 1:
            print(colored("\nuci fw_verion=new","yellow"))
            uci_fw_ver = board.match.group(1)

        print uci_fw_ver
        
        
    def runTest(self):  
        self.uci_getVer()
                
        #Find the admin password
        board.sendline('uci show cameo.cameo.admin_password')
        i = board.expect(["=(\w+)","='(\w+)'"],timeout=15)
        if i == 0:
            print(colored("\nuci admin password=old","yellow"))
            admin_password = board.match.group(1)
        if i == 1:
            print(colored("\nuci admin password=new","yellow"))
            admin_password= board.match.group(1)
        
        print admin_password

        #installers.install_wget(lan)
        
        lan.sendline('wget --http-user=admin --http-password=%s -P /home/ http://192.168.2.1/others/firmware.html' %(admin_password))
        lan.expect('firmware.html',timeout=15)
        lan.expect('Saving to:',timeout=15)
        lan.expect(prompt)
                
        
        lan.sendline('head -n 450 /home/firmware.html |tail -n 20 |grep "<dd>"')
        lan.expect(prompt)
        fw_page_ver = lan.before
        fw_page_ver = fw_page_ver.replace('head -n 450 /home/firmware.html |tail -n 20 |grep "<dd>"','')
        fw_page_ver_result = fw_page_ver.replace('<>','')
                        
        if uci_fw_ver in fw_page_ver_result:
            print '\nPass'
        else:
            msg = "Version is not correctly , The WEBUI version is %s , DUT_FW version is %s " %(fw_page_ver_result , uci_fw_ver)
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Firmware_verCheck_hiddenPage(rootfs_boot.RootFSBootTest):
    '''Version /build number must be correct in hidden page (MTK).'''
    
    def runTest(self):
        product = Product_information_fwupgrade(None)
        product.chklst()
        board.login_elecom()
        board.sendline('uci show|grep cameo.system.fw_version_build')
        board.expect('cameo.system.fw_version_build=(.*)')
        fw_version_build = board.match.group(1)
        fw_version_build = fw_version_build.replace('\'','')
        fw_version_build = fw_version_build.replace('cameo.system.fw_version_build_rc=rc1','')
        fw_version_build = fw_version_build.strip()
        
        if fw_version_build in firmware_version:
            print '\nPass'
        else:
            msg = "Hidden page version is not correctly"
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Firmware_verCheck_Binfile(rootfs_boot.RootFSBootTest):
    '''Version /build number must be correct in BIN file(MTK).'''

    def runTest(self):
        #Get fw_file,fw_file_name
        get_file = Firmware_verCheck_releasenote(None)
        get_file.find_filename()
        fw_file_name_r = fw_file_name.replace('.bin','').replace('_',' ')#remove '.bin' and '_'

        binfile = []
        f = open(fw_file,'r')
        for line in f.readlines()[0:1]:
            line = line.strip()
            str(binfile.append(str(line)))
        f.close()
        binfile = "".join(binfile)#list to str

        if fw_file_name_r in binfile:
            print '\nPass'
        else:
            print '\nFail'
            msg = "Bin file does not match the ver/build number"
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

       
class Firmware_verCheck_MD5CheckSum(rootfs_boot.RootFSBootTest):
    '''The MD5 Checksum of compared firmware file must be the same as build log (MTK).'''


    def runTest(self):
        import hashlib        
        #Get fw_file, releasenote
        get_file = Firmware_verCheck_releasenote(None)
        get_file.find_filename()

        #Get fw_date from chklst
        product = Product_information_fwupgrade(None)
        product.chklst()
                 
        #Get fw_date from uci command
        board.login_elecom()
        board.sendline('uci get cameo.system.fw_date')
        board.expect('(\d+, \w+, \d+)')
        fw_date = board.match.group(1)
        print fw_date

        #Measure the MD5
        m = hashlib.md5()
        with open(fw_file, "rb") as f:
            buf =f.read()
            m.update(buf)
        fw_md5_result = m.hexdigest()
        
        
        if fw_date in releasenote:
            if fw_md5_result in releasenote:
                print '\nfw_date - Passed!'
                print '\nfw_md5 - Passed!'
            else:
                print '\nfw_date - Passed!'
                print '\nfw_md5 - Failed!'
                msg = "fw_md5 is not correctly"
                self.result_message = msg + ',The result is %s' %(fw_md5_result)
                raise Exception (msg)

        else:
            if fw_md5_result in releasenote:
                print '\nfw_date - Failed!'
                print '\nfw_md5 - Passed!'
                msg = "fw_date is not correctly"
                self.result_message = ',The result is %s' %(fw_date)
                raise Exception (msg)
            else:
                print '\nfw_date & fw_md5 - Failed!'
                msg = "checksum and fw_file_name are not correctly,"
                self.result_message = msg + 'The result is %s , %s' %(fw_date, fw_md5_result )
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')



class Channel_list(rootfs_boot.RootFSBootTest):
    '''WiFi Channel list must match latest specification(MTK).'''

    def runTest(self):
        #For japan's channel list
        wlan0_ch_spec = "['1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13']"
        wlan1_ch_spec_old = "['36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 132, 136, 140']"
        wlan1_ch_spec_new = "['36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140']"

        product = Product_information_fwupgrade(None)
        product.chklst()


        if wlan0_ch == wlan0_ch_spec:
            if wlan1_ch == wlan1_ch_spec_old: 
                print '\n2G channel list - Passed!'
                print '\n5G channel list - Passed!'
            else:
                print '\n2g channel list - Passed!'
                print '\n5g channel list - Failed!'
                print(colored("\nOld spec of 5G Channel failed! , Starting compare to new spec","yellow"))
                
                if wlan1_ch == wlan1_ch_spec_new:
                    print(colored("\nCompare to new spec - Passed","yellow"))       
                    msg = "5G Channel list match the new spec"
                    self.result_message = msg + ',The result is %s' %(wlan1_ch)
                else:
                    msg = "5G Channel list does not match the spec"
                    self.result_message = msg + ',The result is %s' %(wlan1_ch)
                    raise Exception (msg)

        else:
            if wlan1_ch == wlan1_ch_spec_old:
                print '\n2G channel list - Failed!'
                print '\n5G channel list - Passed!'
                msg = "2G Channel list does not match the spec"
                self.result_message = msg + ',The result is %s' %(wlan0_ch)
                raise Exception (msg)
            else:
                print '\n2G & 5G channel - Failed!'
                print(colored("\nOld spec of 5G Channel failed! , Starting compare to new spec","yellow"))
                
                if wlan1_ch == wlan1_ch_spec_new:
                    print(colored("\nCompare to new spec - Passed","yellow"))
                    msg = "2G Channel list does not match the spec , 5G Channel list match the new spec"
                    self.result_message = msg + ',The result is %s' %(wlan0_ch)
                    raise Exception (msg)
                else:
                    msg = "2G & 5G Channel list does not match the spec"
                    self.result_message = msg + ',The result is %s , %s' %(wlan0_ch, wlan1_ch)
                    raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')




class SingleSKU_MD5(rootfs_boot.RootFSBootTest):
    '''Check MD5SUM for SingleSKU (MTK).'''
    def runTest(self):
        #Get releasenote
        get_file = Firmware_verCheck_releasenote(None)
        get_file.find_filename()
        
        board.login_elecom()
        board.check_output('md5sum /etc_ro/Wireless/RT2860AP/7615_SingleSKU.dat')
        md5sku = re.findall(r'[a-fA-F\d]{32}',board.before)
        md5sku = "".join(md5sku) # list to str

        board.check_output('md5sum /etc_ro/Wireless/RT2860AP/7615_SingleSKU_BF.dat')
        md5sku_bf = re.findall(r'[a-fA-F\d]{32}',board.before)
        md5sku_bf = "".join(md5sku_bf) # list to str
        

        if md5sku in releasenote:
            if md5sku_bf in releasenote:
                print(colored("\nmd5sku - Passed!","yellow"))
                print(colored("\nmd5sku_bf - Passed!","yellow"))
            else:
                print(colored("\nmd5sku - Passed!","yellow"))
                print(colored("\nmd5sku_bf - Failed!","red"))           
                msg = "md5sku_bf is not correctly"
                self.result_message = msg + ', The result is %s' %(md5sku)
                raise Exception (msg)

        else:
            if md5sku_bf in releasenote:
                print(colored("\nmd5sku - Failed!","red"))
                print(colored("\nmd5sku_bf - Passed!","yellow"))
                msg = "md5sku_bf is not correctly"
                self.result_message = msg + ', The resultis %s' % (md5sku_bf)
                raise Exception (msg)
            else:
                print(colored("\nAll are not correctly ,Please check releasenote or md5sku and md5skubf is not include it","red"))
                msg = "All are not correctly ,Please check releasenote or md5sku and md5skubf is not include it "
                self.result_message = msg + ', The result is  %s , %s' %(md5sku, md5sku_bf)
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')



class Default_value_SSID(rootfs_boot.RootFSBootTest):
    '''Default SSID must match customer's requirement (MTK).'''

    def runTest(self):
        #Get Mac address from ifconfig
        interface = 'br-lan'
        board.login_elecom()
        board.sendline('ifconfig %s' % interface)
        board.expect('HWaddr (.\w.*)')
        br_lan = board.match.group(1)
        board.expect(prompt)        
        br_lan = (br_lan[9:17]) #Get mac address from last 8 bit
        br_lan = br_lan.replace(':','')
        br_lan_essid = 'elecom-'+br_lan.lower()# str to lower

        #Get SSID from iwconfig
        interface_wifi = 'ra0'
        board.sendline('iwconfig %s |grep ESSID' % interface_wifi)
        board.expect('ESSID:"(.*)"')
        iwconfig_essid = board.match.group(1)
        board.expect(prompt)
        
        if iwconfig_essid == br_lan_essid:
            print '\nPass'
        else:
            print '\nFail'
            msg = "The DUT SSID does not match the customer requirement"
            self.result_message = msg + ', DUT=%s , Requitement=%s' % (iwconfig_essid, br_lan_essid)
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')



class Default_value_WifiPSK(rootfs_boot.RootFSBootTest):
    '''Default WiFi PSK and authentication type must match customer's requirement (MTK).'''

    def runTest(self):

        board.login_elecom()
        #wlan0 security default = wpa2_psk
        board.sendline('uci show qcawifi_router.wlan0.vap0_security')
        board.expect('qcawifi_router.wlan0.vap0_security=(\D.+)root')# capture reuslt and end to root@wrc...
        wlan0_security = board.match.group(1)
        wlan0_security = wlan0_security.replace('\'','').strip()

        #wlan0 cipher type default = aes
        board.sendline('uci show qcawifi_router.wlan0.vap0_psk_cipher_type')
        board.expect('qcawifi_router.wlan0.vap0_psk_cipher_type=(\D.+)root')# capture reuslt and end to root@wrc...
        wlan0_cipher_type = board.match.group(1)
        wlan0_cipher_type = wlan0_cipher_type.replace('\'','').strip()

        #wlan1 security default = wpa2_psk
        board.sendline('uci show qcawifi_router.wlan0.vap1_security')
        board.expect('qcawifi_router.wlan0.vap1_security=(\D.+)root')# capture reuslt and end to root@wrc...
        wlan1_security = board.match.group(1)
        wlan1_security = wlan1_security.replace('\'','').strip()

        #wlan1 cipher type default = aes
        board.sendline('uci show qcawifi_router.wlan1.vap0_psk_cipher_type')
        board.expect('qcawifi_router.wlan1.vap0_psk_cipher_type=(\D.+)root')# capture reuslt and end to root@wrc...
        wlan1_cipher_type = board.match.group(1)
        wlan1_cipher_type = wlan1_cipher_type.replace('\'','').strip()
        
        

        if 'wpa2_psk' in wlan0_security and 'aes' in wlan0_cipher_type and 'wpa2_psk' in wlan1_security and 'aes' in wlan1_cipher_type: 
            print '\nPass'
        else:
            print '\nFail'
            msg = "Default Wifi PSK or authentication type does not match the spec"
            self.result_message = msg + ", wlan0=%s %s, wlan1=%s %s " %(wlan0_security, wlan0_cipher_type,wlan1_security, wlan1_cipher_type)
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Default_value_LANIP(rootfs_boot.RootFSBootTest):
    '''Default LAN IP must match customer's requirement (MTK).'''

    def runTest(self):
        
        board.login_elecom()
        board.sendline('uci get network_router.lan.ipaddr')
        board.expect('(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
        lanip = board.match.group(1)
        
        if '192.168.2.1' in lanip:
            print '\nPass'
                                    
        else:
            print '\nFail'
            msg = "LAN IP does not match the customer's requirement"
            self.result_message = msg+ ", LANIP=%s" % lanip
            raise Exception (msg)


    def recover(self):
        board.sendcontrol(']')

  
class Default_value_WANtype(rootfs_boot.RootFSBootTest):
    '''Default WAN type must match customer's requirement(MTK).'''

    def runTest(self):
        board.login_elecom()
        board.sendline('uci get network_router.wan.proto')
        board.expect('dhcp')# capture reuslt
        wantype = board.match.group(0)
                
        if 'dhcp' in wantype:
            print '\nPass'
        else:
            print '\nFail'
            msg = "WAN type does not match the customer's requirement"
            self.result_message = msg+ ", WANtype=%s" % wantype
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

