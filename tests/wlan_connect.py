# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

# History
# 2019/1/30 New feature for Wlan_Connect_2g
# 2019/2/12 Add wpa_supplicant
# 2019/2/14 New Feature for Wlan_Connect_5g
# 2019/2/18 Add routing when obtioning the IP address
# 2019/2/19 Add of kill the wlan_supplicant process if is exist
# 2019/3/20 1.Add if failed to connect to DUT , modify the retry times
#           2.Add ifconfig wlan0 down after recover mode
#           3.Fine tune the process
# 2019/4/22 Mofify SSID get from UCI and transfom changed


import re
import rootfs_boot
import time
from devices import board, wan, lan, wlan, prompt
from lib import installers

class Wlan_Connect_2g(rootfs_boot.RootFSBootTest):
    '''EOL - Wlan 2g client connect to DUT.'''

    def disconnect_wifi(self):
        wlan.sendline('killall wpa_supplicant')
        wlan.expect(prompt)
        wlan.sendline('ifconfig wlan0 down')
        wlan.expect(prompt)
    
    def wpa_supplicant(self):
        wlan.sendline('killall wpa_supplicant')
        wlan.expect(prompt)
        wlan.sendline('wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf')
        wlan.expect('Successfully')
        wlan.expect(prompt)
        wlan.sendline('dhclient -r wlan0')
        wlan.expect(prompt)
        wlan.sendline('dhclient wlan0')
        wlan.expect(prompt)        
        print ('\nConnecting to DUT , Please Wait')
        time.sleep(5)

        
    def ping_status(self):
        global n
        #ping router ip
        router_ip = board.get_interface_ipaddr(board.lan_iface)
        lan.sendline('\nping -c 5 %s' % router_ip)
        lan.expect('PING ') 
        lan.expect(' ([0-9]+) (packets )?received')
        n = int(lan.match.group(1))
        lan.expect(prompt)                 
    
    def runTest(self):
       
        #initail the interface
        wifi_card_interface = 'wlan0'
        wlan2g_iface = 'ra0'        
        #installers.install_wpa_supplicant(wlan)
        wlan.sendline('\nroute del default gw 10.0.0.1')
        wlan.expect(prompt)
        wlan.sendline('\nroute -n')
        wlan.expect(prompt)


        #Get board information for SSID and password
        board.sendline('fw_printenv')
        board.expect('wlan0_key=(\d+\w*)')
        wifi_2g_password = board.match.group(1)

        #board.sendline('iwconfig %s' % wlan2g_iface)
        #board.expect('ESSID:"(.*)"')
        board.sendline('uci get qcawifi_router.wlan0.vap0_ssid')
        board.expect('elecom-\w{6}')#get ssid elecom-6digit
        wifi_2g_ssid = board.match.group(0)
        #wifi_2g_ssid = wifi_2g_ssid.replace('\'','')

        #Write the profile to wlan     
        wlan.sendline('''cat > /etc/wpa_supplicant.conf << EOF
ctrl_interface=/var/run/wpa_supplicant
update_config=1
network={
    ssid="%s"
    psk="%s"
}
EOF''' % (wifi_2g_ssid, wifi_2g_password))
        wlan.expect(prompt)
        wlan.sendline('ifconfig eth1 down')
        wlan.expect(prompt)
        wlan.sendline('rm -rf /var/run/wpa_supplicant/')
        wlan.expect(prompt)
        wlan.sendline('ifconfig %s down' % wifi_card_interface)
        wlan.expect(prompt)
        time.sleep(2)
        wlan.sendline('ifconfig %s up' % wifi_card_interface)
        wlan.expect(prompt)
        time.sleep(2)
        wlan_status = wlan.before
        print wlan_status
        if 'Connection' in wlan_status:
            print('Skipping test due to wlan not link up')
            self.skipTest("Skipping test no wlan0")
       
        self.wpa_supplicant()                
        self.ping_status()
        if n > 3:
            print 'Connected to DUT'
            self.disconnect_wifi()#disconnect the wlan
        else:
            for i in range(3):# retry times 
                self.wpa_supplicant() 
                self.ping_status()
                if n > 3:
                    self.disconnect_wifi()#disconnect the wlan after succeed
                    break
                else:
                    i = i + 1
                    print '\nConnecting failed , Retry for %s times' %i


        
    def recover(self):
        wlan.sendline('killall wpa_supplicant')
        wlan.expect(prompt)
        wlan.sendline('ifconfig wlan0 down')
        wlan.expect(prompt)




class Wlan_Connect_5g(rootfs_boot.RootFSBootTest):
    '''EOL - Wlan 5g client connect to DUT.'''
    def disconnect_wifi(self):
        wlan.sendline('killall wpa_supplicant')
        wlan.expect(prompt)
        wlan.sendline('ifconfig wlan0 down')
        wlan.expect(prompt)
    
    def wpa_supplicant(self):
        wlan.sendline('killall wpa_supplicant')
        wlan.expect(prompt)
        wlan.sendline('wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf')
        wlan.expect('Successfully')
        wlan.expect(prompt)
        wlan.sendline('dhclient -r wlan0')
        wlan.expect(prompt)
        wlan.sendline('dhclient wlan0')
        wlan.expect(prompt)        
        print ('\nConnecting to DUT , Please Wait')
        time.sleep(5)
   
    def ping_status(self):
        global n
        #ping router ip
        router_ip = board.get_interface_ipaddr(board.lan_iface)
        lan.sendline('\nping -c 5 %s' % router_ip)
        lan.expect('PING ') 
        lan.expect(' ([0-9]+) (packets )?received')
        n = int(lan.match.group(1))
        lan.expect(prompt)                  
    
    def runTest(self):
       
        #initail the interface
        wifi_card_interface = 'wlan0'
        wlan5g_iface = 'rai0'        
        #installers.install_wpa_supplicant(wlan)
        wlan.sendline('\nroute del default gw 10.0.0.1')
        wlan.expect(prompt)
        wlan.sendline('\nroute -n')
        wlan.expect(prompt)


        #Get board information for SSID and password
        board.sendline('fw_printenv')
        board.expect('wlan0_key=(\d+\w*)')
        wifi_5g_password = board.match.group(1)

        #board.sendline('iwconfig %s' % wlan5g_iface)
        #board.expect('ESSID:"(.*)"')

        board.sendline('uci get qcawifi_router.wlan1.vap0_ssid')
        board.expect('elecom-\w{6}')#get ssid elecom-6digit
        wifi_5g_ssid = board.match.group(0)

        #Write the profile to wlan
        wlan.sendline('''cat > /etc/wpa_supplicant.conf << EOF
ctrl_interface=/var/run/wpa_supplicant
update_config=1
network={
    ssid="%s"
    psk="%s"
}
EOF''' % (wifi_5g_ssid, wifi_5g_password))
        wlan.expect(prompt)
        wlan.sendline('ifconfig eth1 down')
        wlan.expect(prompt)
        wlan.sendline('rm -rf /var/run/wpa_supplicant/')
        wlan.expect(prompt)
        wlan.sendline('ifconfig %s down' % wifi_card_interface)
        wlan.expect(prompt)
        time.sleep(2)
        wlan.sendline('ifconfig %s up' % wifi_card_interface)
        wlan.expect(prompt)
        time.sleep(2)
        wlan_status = wlan.before
        print wlan_status
        if 'Connection' in wlan_status:
            print('Skipping test due to wlan not link up')
            self.skipTest("Skipping test no wlan0")
        
        self.wpa_supplicant()
        self.ping_status()
        if n > 3:
            print 'Connected to DUT'
            self.disconnect_wifi()#disconnect the wlan after succeed
        else:
            for i in range(3):# retry times
                self.wpa_supplicant()
                self.ping_status()
                if n > 3:
                    self.disconnect_wifi()#disconnect the wlan after succeed
                    break
                else:
                    i = i + 1
                    print '\nConnecting failed , Retry for %s times' %i        

    def recover(self):
        wlan.sendline('killall wpa_supplicant')
        wlan.expect(prompt)
        wlan.sendline('ifconfig wlan0 down')
        wlan.expect(prompt)




