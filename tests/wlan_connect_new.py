# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import re
import rootfs_boot
import time
from devices import board, wan, lan, wlan, prompt
from lib import installers
from devices import power
from termcolor import *
from Sample_basic_function import *

interface_2g = 'apcli0'
interface_5g = 'apclii0'
dut_ip = '192.168.0.1'
internet_ip = '8.8.8.8'
host_pc = '192.168.0.55'

admin ='admin'
password = '12345678a'


class wifi_connect:

    def get_checklist(self):
        #Get SSID from DUT checklst.txt
        #Checklist is default value
        #if you want to get the dynamic , please use the version.txt
        global ssid_2g,ssid_5g,wifi_pw_2g,wifi_pw_5g
        lan.sendline("wget http://192.168.0.1/chklst.txt -o /tmp/get_chklst.log")
        lan.expect(prompt)
                
        chklst = lan.check_output('cat chklst.txt')
        chklst = chklst.replace('<br>','')
        
        #chklst = lan.before.replace('<br>','')
        #Get SSID
        ssid_2g = re.findall('SSID: (\w.*)',chklst)
        ssid_5g = re.findall('SSID_1: (\w.*)',chklst)
        ssid_2g  = "".join(ssid_2g).strip()
        ssid_5g  = "".join(ssid_2g).strip()
        #Get password
        #lan mac last 4 bit + 1234
        #example 6C:19:8F:F4:67:45 6745+1234
        lan_mac = re.findall('LAN MAC: (\w.*)',chklst)
        lan_mac = "".join(lan_mac).strip()
        default_pw = lan_mac[-5:].replace(':','') + '1234'
        wifi_pw_2g = default_pw
        wifi_pw_5g = default_pw
        
        #Get channel list
        global wlan0_ch,wlan1_ch
        wlan0_ch = re.findall('WLAN 0 Channel List: (\d.*)',chklst)
        wlan1_ch = re.findall('WLAN 1 Channel List: (\d.*)',chklst)
        wlan0_ch = "".join(wlan0_ch).strip()
        wlan1_ch = "".join(wlan1_ch).strip()
               
    def connection_check(self):
        #Check wifi connection
        global connection_check
        try:
            i = board.expect(["AndesLedEnhanceOP: Success"], timeout=30)
            if i == 0:
                board.sendline('\n\n\n')
                board.expect(prompt) 
                print(colored("\nConnected the DUT","yellow"))
                connection_check = 'Pass'
            else:
                print(colored("\nConnection Failed","red"))
                connection_check = 'Fail'
                
        except:
            print(colored("\nConnection Failed","red"))
            connection_check = 'Fail'
     
    def brctl_check(self):
        #Check brctl interface for ipaddress
        board.sendline('\nclear')
        board.expect(prompt)
        board.sendline('brctl show > /tmp/brctl.txt')
        board.expect(prompt)

        while True:
            try:
                board.sendline("\ncat /tmp/brctl.txt")
                i = board.expect(['apcli0'],timeout=10)
                if i == 0:
                    print(colored("\nFound apcli0 inteface","yellow"))
                    break
                    
            except:
                print(colored("\nNot Found apcli0 , Now adding wifi interface","red"))
                board.sendline('brctl addif br-lan %s' % (interface_2g)) #bridge the 2g interface
                board.expect(prompt)
                board.sendline('brctl addif br-lan %s' % (interface_5g)) #bridge the 5g interface
                board.expect(prompt)   
                board.sendline('\n\n\n')
                board.expect(prompt)
                break


    def send_wpa2_aes(self):
        #Send command to station with wpa2_aes
        if 'smart2g' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=WPA2PSK' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=AES' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_2g,ssid_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliWPAPSK=%s' % (interface_2g,wifi_pw_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_2g))
            board.expect(prompt)
            print(colored("\nConnecting WIFI with WPA2 AES , Please Wait","yellow"))
         
        elif 'smart5g' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=WPA2PSK' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=AES' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_5g,ssid_5g))        
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliWPAPSK=%s' % (interface_5g,wifi_pw_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_5g))
            board.expect(prompt)
            print(colored("\nConnecting WIFI with WPA2 AES , Please Wait","yellow"))
        
        elif 'default' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=WPA2PSK' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=AES' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid= ' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliWPAPSK= ' % (interface_2g))
            board.expect(prompt)
            print(colored("\nReset to default WIFI SSID and Password","yellow"))
    
    def send_wpa_tkip(self):
        #Send command to station with wpa2_tkip
        if 's2g_wpatkip' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=WPAPSK' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=TKIP' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_2g,ssid_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliWPAPSK=%s' % (interface_2g,wifi_pw_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_2g))
            board.expect(prompt)
            print(colored("\nConnecting WIFI with WPA TKIP , Please Wait","yellow"))
         
        elif 's5g_wpatkip' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=WPAPSK' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=TKIP' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_5g,ssid_5g))        
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliWPAPSK=%s' % (interface_5g,wifi_pw_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_5g))
            board.expect(prompt)
            print(colored("\nConnecting WIFI with WPA TKIP , Please Wait","yellow"))

    def send_none(self):
        #Send command to station with none
        if 's2g_none' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=OPEN' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=NONE' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_2g,ssid_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_2g))
            board.expect(prompt)
            print(colored("\nConnecting WIFI with NONE , Please Wait","yellow"))
         
        elif 's5g_none' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=OPEN' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=NONE' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_5g,ssid_5g))        
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_5g))
            board.expect(prompt)
            print(colored("\nConnecting WIFI with NONE , Please Wait","yellow"))
           
    def Mode802_11(self):
        # 802.11 2g mode
        if 'n1' in command_802_mode:
            print(colored("\nConfigure 802.11n of wlan0","yellow"))
            board.sendline('uci set qcawifi.wlan0.dot11_mode=11n')
            board.expect(prompt)

        elif 'g2' in command_802_mode:
            print(colored("\nConfigure 802.11g of wlan0","yellow"))
            board.sendline('uci set qcawifi.wlan0.dot11_mode=11g')
            board.expect(prompt)

        elif 'b3' in command_802_mode:
            print(colored("\nConfigure 802.11b of wlan0","yellow"))
            board.sendline('uci set qcawifi.wlan0.dot11_mode=11b')
            board.expect(prompt)

        # 802.11 5g mode
        elif 'ac6' in command_802_mode:
            print(colored("\nConfigure 802.11ac of wlan1","yellow"))
            board.sendline('uci set qcawifi.wlan1.dot11_mode=11ac')
            board.expect(prompt)

        elif 'n5' in command_802_mode:
            print(colored("\nConfigure 802.11n of wlan1","yellow"))
            board.sendline('uci set qcawifi.wlan1.dot11_mode=11n')
            board.expect(prompt)

        elif 'a4' in command_802_mode:
            print(colored("\nConfigure 802.11a of wlan1","yellow"))
            board.sendline('uci set qcawifi.wlan1.dot11_mode=11a')
            board.expect(prompt)

        elif 'default' in command_802_mode:
            print(colored("\nConfigure 802.11bgn of wlan0","yellow"))
            board.sendline('uci set qcawifi.wlan0.dot11_mode=11bgn')
            board.expect(prompt)

            print(colored("\nConfigure 802.11ac of wlan1","yellow"))
            board.sendline('uci set qcawifi.wlan1.dot11_mode=11ac')
            board.expect(prompt)

        board.sendline('uci commit')
        board.expect(prompt,timeout=30)
        board.sendline('wlan_config.sh stop')
        board.expect(prompt,timeout=30)
        board.sendline('wlan_config.sh boot')
        board.expect(prompt,timeout=30)
        print(colored("\n802.11mode is configured and Wlan_Reboot Success","yellow"))
        
    def get_bit_rate_2g(self):
        global bit_rate        
        n = 0
        while True:
            try:       
                board.sendline('\nclear')
                board.expect(prompt)
                board.sendline('iwconfig %s' % (interface_2g))
                board.expect('Bit Rate[:=]([^ ]+)')
                bit_rate = board.match.group(1)
                bit_rate = bit_rate.strip()
                if int(bit_rate) <= 1000:
                    print(colored("\nBit Rate=%s" %bit_rate,"yellow"))
                    break
                else:
                    n = n + 1
                    print(colored("\nBit Rate Error , Retry %s" %n,"yellow"))
                    if n > 3:
                        break
            except:
                print(colored("\nBit Rate Error , Retry again" ,"yellow"))

     
    def get_bit_rate_5g(self):
        global bit_rate        
        n = 0
        while True:
            try:                
                board.sendline('\nclear')
                board.expect(prompt)
                board.sendline('iwconfig %s' % (interface_5g))
                board.expect('Bit Rate[:=]([^ ]+)')
                bit_rate = board.match.group(1)
                bit_rate = bit_rate.strip()
                if float(bit_rate) <= 2000:
                    print(colored("\nBit Rate=%s" %bit_rate,"yellow"))
                    break
                else:
                    n = n + 1
                    print(colored("\nBit Rate Error , Retry %s" %n,"yellow"))
                    if n > 3:
                        break
            except:
                print(colored("\nBit Rate Error , Retry again" ,"yellow"))

    def ip_routing_main(self):
        #Must manual configure to ipaddress / routing
        #ip 192.168.0.1
        board.sendline('\nclear')
        board.expect(prompt)
        board.sendline('ip addr flush dev br-lan')
        board.expect(prompt)
        board.sendline('ip addr add 192.168.0.168/24 dev br-lan')
        board.expect(prompt)
        board.sendline('route add default gw 192.168.0.1')
        board.expect(prompt)
        print(colored("\nConfigure IP routing","yellow"))
    
    def ip_routing_guest(self):
        #Must manual configure to ipaddress / routing
        #ip 192.168.7.1
        board.sendline('\nclear')
        board.expect(prompt)
        board.sendline('ip addr flush dev br-lan')
        board.expect(prompt)
        board.sendline('ip addr add 192.168.0.168/24 dev br-lan')
        board.expect(prompt)
        board.sendline('route add default gw 192.168.0.1')
        board.expect(prompt)
        print(colored("\nConfigure IP routing","yellow"))
    
    def get_ssid_2g(self):
        #Client get ssid2g
        global ssid_2g_status,iw_ssid_2g
        while True:
            try:
                board.sendline('\nclear')
                board.expect(prompt)
                board.sendline('iwconfig %s |grep ESSID' % (interface_2g))
                board.expect('ESSID:"(.*)"')
                iw_ssid_2g = board.match.group(1)
                iw_ssid_2g = iw_ssid_2g.strip()
         
                if iw_ssid_2g == ssid_2g:
                    ssid_2g_status = 'Pass'
                    print(colored("\nPass , The same with DUT Config","yellow"))
                    break
                else:
                    ssid_2g_status = 'Fail'
                    print(colored("\nFail , Not same with DUT Config","red"))
                    break
            except:
                print(colored("\nError command","red"))

    def get_ssid_5g(self):
        #Client get ssid5g
        global ssid_5g_status,iw_ssid_5g
        while True:
            try:
                board.sendline('\nclear')
                board.expect(prompt)
                board.sendline('iwconfig %s |grep ESSID' % (interface_5g))
                board.expect('ESSID:"(.*)"')
                iw_ssid_5g = board.match.group(1)
                iw_ssid_5g = iw_ssid_5g.strip()

                if iw_ssid_5g == ssid_5g:
                    ssid_5g_status = 'Pass'
                    print(colored("\nPass , The same with DUT Config","yellow"))
                    break
                else:
                    ssid_5g_status = 'Fail'
                    print(colored("\nFail , Not same with DUT Config","red"))
                    break
            except:
                print(colored("\nError command","red"))

    def get_channel_2g(self):
        #Client get channel 2g
        global ch_2g
        n = 0
        while True:
            try:
                board.sendline('\nclear')
                board.expect(prompt)
                board.sendline('iwconfig %s |grep Channel' % (interface_2g))
                i = board.expect(['Channel=(\d+)'],timeout=10)
                if i == 0:
                    ch_2g = board.match.group(1)
                    ch_2g = ch_2g.strip()
                    board.expect(prompt)
                    print(colored("\n2G WIFI Channel is '%s'" % ch_2g,"yellow")) 
                    break
                else:
                    n = n + 1
                    if n > 10:
                        print(colored("\nRetry to get Channel , Retry %s" %n,"yellow"))
                        break
            except:
                print(colored("\nError command","red"))
                    
    def get_channel_5g(self):
        #Client get channel 5g
        global ch_5g
        n = 0
        while True:
            try:
                board.sendline('\nclear')
                board.expect(prompt)
                board.sendline('iwconfig %s |grep Channel' % (interface_5g))
                i = board.expect(['Channel=(\d+)'],timeout=10)
                if i == 0:
                    ch_5g = board.match.group(1)
                    ch_5g = ch_5g.strip()
                    board.expect(prompt)
                    print(colored("\n5G WIFI Channel is '%s'" % ch_5g,"yellow"))
                    break
                else:
                    n = n + 1
                    if n > 10:
                        print(colored("\nRetry to get Channel , Retry %s" %n,"yellow"))
                        break
            except:
                print(colored("\nError command","red"))

    def get_ipaddress(self):
        #Client get IPaddress
        global ipaddress
        while True:
            try:
                board.sendline('\nclear')
                board.expect(prompt)
                board.sendline('ifconfig br-lan |grep inet')
                board.expect('inet addr:(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
                ipaddress = board.match.group(1)
                ipaddress = ipaddress.strip()
                board.expect(prompt)
                print(colored("\nWIFI Client IPAddress is '%s'" % ipaddress,"yellow"))
                print(colored("\nWaiting for DUT Configure 10 sec","yellow"))
                time.sleep(10)
                break
            except:
                print(colored("\nError command","red"))
        
    def PingDUT(self):
        #Client Ping DUT
        global ping_dut_result
        j = 0 
        while True:
            board.sendline('\nclear')
            board.expect(prompt)
            board.sendline('\nping -c5 -W 1 %s > /tmp/ping_dut.txt' % (dut_ip))
            board.expect(prompt, timeout=10)
            board.sendline('\nclear')
            board.expect(prompt)
            
            try:
                board.sendline('\ncat /tmp/ping_dut.txt |grep received')
                i = board.expect([' ([0-5]+) (packets )?received','No such file or directory','Network is unreachable'],timeout=10)      
                if i == 0:
                    n = int(board.match.group(1))
                    board.expect(prompt)
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
    
    def PingDUT_Status(self):
        #if failed , will retry 3 times
        n = 0
        while True:
            if 'Fail' in ping_dut_result:
                n = n + 1
                print(colored("\nPing DUT Status Check Fail , Retry again %s" %n,"yellow"))
                self.PingDUT()
                if n > 3:
                    break
            else:
                print(colored("\nPing DUT Status Check OK","yellow"))
                break
    
    def PingDUT_Guest(self):
        #Transfer the result to guest zone
        global ping_dut_result

        if 'Fail' in ping_dut_result:
            ping_dut_result = 'Pass'
        else:
            ping_dut_result = 'Fail'

    def PingHost_PC(self):
        #Client Ping Host PC
        global ping_hostpc_result
        j = 0 
        while True:
            board.sendline('\nclear')
            board.expect(prompt)
            board.sendline('\nping -c5 -W 1 %s > /tmp/ping_hostpc.txt' % (host_pc))
            board.expect(prompt, timeout=10)
            board.sendline('\nclear')
            board.expect(prompt)
            
            try:
                board.sendline('\ncat /tmp/ping_hostpc.txt |grep received')
                i = board.expect([' ([0-5]+) (packets )?received','No such file or directory','Network is unreachable'],timeout=10)      
                if i == 0:
                    n = int(board.match.group(1))
                    board.expect(prompt)
                    if n > 0:
                        ping_hostpc_result= 'Pass'
                        print(colored("\nPing HostPC OK","yellow"))
                        break
                    else:
                        ping_hostpc_result= 'Fail'
                        print(colored("\nPing HostPC Fail","red"))
                        break

                if i == 1:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow")) 
                    if j > 10:
                        ping_hostpc_result = 'Fail'
                        break

                if i == 2:
                    j = j + 1
                    print(colored("\nUnable to get IP , Retry %s" %j,"yellow"))
                    if j > 10:
                        ping_hostpc_result = 'Fail'
                        break
            except:
                ping_hostpc_result= 'Fail'
                print(colored("\nPing HostPC Fail","red"))
    
    def PingHost_PC_Guest(self):
        #Transfer the result to guest zone
        global ping_hostpc_result

        if 'Fail' in ping_hostpc_result:
            ping_hostpc_result = 'Pass'
        else:
            ping_hostpc_result = 'Fail'
    
    def PingInternet(self):
        #Client Ping Internet
        global ping_internet_result
        j = 0
        k = 0
        while True:
            board.sendline('\nclear')
            board.expect(prompt)
            board.sendline('\nping -c5 -W 1 %s > /tmp/ping_internet.txt'%(internet_ip))
            board.expect(prompt, timeout=10)
            board.sendline('\nclear')
            board.expect(prompt)
            
            try:
                board.sendline('\ncat /tmp/ping_internet.txt |grep received')
                i = board.expect([' ([0-5]+) (packets )?received','No such file or directory','Network is unreachable'],timeout=10)
                if i == 0:
                    n = int(board.match.group(1))
                    board.expect(prompt)
                    if n > 0:
                        ping_internet_result = 'Pass'
                        print(colored("\nPing Internet OK","yellow"))
                        break
                    else:
                        ping_internet_result = 'Fail'
                        print(colored("\nPing Internet Fail","red"))
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
                        ping_internet_result = 'Get IP Fail'
                        break

                else:
                    k = k + 1
                    print(colored("\nMore message is not able to read, Retry %s" %k,"yellow"))
                    if k > 10:
                        ping_internet_result = 'Other Fail'
                        break
            except:
                ping_internet_result = 'Fail'
                print(colored("\nPing Internet Fail - Other issue","red"))
   
    def PingInternet_Status(self):
        #if failed , will retry 3 times
        n = 0
        while True:
            if 'Fail' in ping_internet_result:
                n = n + 1
                print(colored("\nPing Internet Status Check Fail , Retry again %s" %n,"yellow"))
                self.PingInternet()
                if n > 3:
                    break
            else:
                print(colored("\nPing Internet Status Check OK","yellow"))
                break

    def BrowseWebUI(self):
        #Client browse the WEBUI
        global browse_webui_result    
        j = 0
        while True:
            board.sendline('\nclear')
            board.expect(prompt)
            board.sendline('\ncurl -I -A Chrome/74.0.3729.157 -m 5 http://%s > /tmp/browse_webui.txt -u %s:%s' %(dut_ip,admin,password))
            board.expect(prompt, timeout=30)
            
            try:
                board.sendline('\ncat /tmp/browse_webui.txt |grep HTTP')
                i = board.expect(["HTTP/1.1 ([200]+)","No such file or directory","cat: can't open","No route to host"],timeout=10)
                if i == 0:
                    n = int(board.match.group(1))
                    board.expect(prompt)
                    if n == 200:
                        browse_webui_result = 'Pass'
                        print(colored("\nBrowse WEBUI OK","yellow"))
                        break
                    else:
                        browse_webui_result = 'Fail'
                        print(colored("\nBrowse WEBUI Fail","red"))
                        break

                if i == 1:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Fail'
                        break

                if i == 2:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Fail'
                        break

                if i ==3:
                    j = j + 1
                    print(colored("\nNo route to host , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Fail'
                        break
                else:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Fail'
                        break
            except:
                j = j + 1
                browse_webui_result = 'Fail'
                print(colored("\nBrowse WEBUI Fail - Nothing","red"))
                if j > 2:
                    break
  
    def BrowseWebUI_Status(self):
        #if failed , will retry 3 times
        n = 0
        while True:
            if 'Fail' in browse_webui_result:
                n = n + 1
                print(colored("\nBrowse WebUI Status Check Fail , Retry again %s" %n,"yellow"))
                self.BrowseWebUI()
                if n > 3:
                    break
            else:
                print(colored("\nBrowse WebUI Status Check OK","yellow"))
                break

    def BrowseWebUI_Guest(self):
        #Transfer the result to guest zone
        
        global browse_webui_result
        if 'Fail' in browse_webui_result:
            browse_webui_result = 'Pass'
        else:
            browse_webui_result = 'Fail'


    def restart(self):
        #Restart board
        board.sendline('\n\n\n')
        board.expect(prompt)
        board.sendline('reboot')
        board.expect('Restarting system',timeout=15)
        board.wait_for_linux()
        
        #Append DNS info 
        board.sendline("echo 'nameserver 8.8.8.8' >> /etc/resolv.conf")
        board.expect(prompt)

    def firstboot(self):        
        #DUT(wlan) reset to default
        print 'DUT will staring to default, please wait!!!'
        board.sendline('\n\n\n')
        board.expect(prompt)      
        board.sendline('firstboot')
        board.expect('Reset default process is finished')
        board.expect(prompt,timeout=15)
        board.sendline('reboot')
        board.expect('Restarting system',timeout=15)
        board.wait_for_linux()

    def disconnect(self):
        #Disconnect and interface / Restart the interface
        #Add statement if something wrong in DUT
        board.sendline('iwpriv %s set ApCliEnable=0' % (interface_2g))
        board.expect(prompt)
        #i = board.expect(['RTMPRemoveRepeaterEntry.CliIdx=0'] + prompt ,timeout=10)
        #if i == 0:
        #    print(colored("\nStation Need to Reboot now due to something wrong, Please Wait for a while","red"))
        #    board.sendline('reboot')
        #    board.expect('Restarting system',timeout=15)
        #    board.wait_for_linux()
        #else:
        board.sendline('iwpriv %s set ApCliEnable=0' % (interface_5g))
        board.expect(prompt)
        board.sendline('ifconfig %s down' % (interface_2g))
        board.expect(prompt)
        board.sendline('ifconfig %s down' %(interface_5g))
        board.expect(prompt)
        board.sendline('ifconfig %s up' % (interface_2g))
        board.expect('Generate UUID for apidx',timeout=50)
        board.expect(prompt)
        time.sleep(5)
        print(colored("\nRestarting WIFI interface apcli0","yellow"))
        board.sendline('\n\n\n')
        board.expect(prompt)
        board.sendline('ifconfig %s up' % (interface_5g))
        board.expect('Generate UUID for apidx',timeout=50)
        board.expect(prompt)
        time.sleep(5)
        print(colored("\nRestarting WIFI internface apclii0","yellow"))
        board.sendline('\n\n\n')
        board.expect(prompt)
    
    def disconnect_2g(self):
        board.sendline('iwpriv %s set ApCliEnable=0' % (interface_2g))
        board.expect(prompt)

    def disconnect_5g(self):
        board.sendline('iwpriv %s set ApCliEnable=0' % (interface_5g))
        board.expect(prompt)

    def wifi_result(self):
        #Check WIFI Result
        
        global wifi_result
        msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s' % (ping_dut_result,ping_internet_result,browse_webui_result)
        if ping_dut_result == ping_internet_result == browse_webui_result:
            print(colored("\nWIFI Result Pass","yellow"))
            wifi_result = 'Pass'
            
        else:
            print(colored("\nWIFI Result Failed with some items","red"))
            print(colored("\n%s" %msg,"yellow"))
            wifi_result = 'Fail'   
    
    def wifi_result_guest(self):
        #Check WIFI Result

        global wifi_result
        msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s , PingHostPC=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,ping_hostpc_result)
        if ping_dut_result == ping_internet_result == browse_webui_result == ping_hostpc_result:
            print(colored("\nWIFI Result Pass","yellow"))
            wifi_result = 'Pass'
            
        else:
            print(colored("\nWIFI Result Failed with some items","red"))
            print(colored("\n%s" %msg,"yellow"))
            wifi_result = 'Fail'

#--------------------For Dlink--------------------

class Sample_WIFI_ChannelList(rootfs_boot.RootFSBootTest):
    '''WIFI 2G/5G Channel list Check '''

    def runTest(self):
        wifi = wifi_connect()
        wifi.get_checklist()
        
        wlan0_ch_spec = "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11"
        wlan1_ch_spec = "36, 40, 44, 48, 149, 153, 157, 161, 165"

        if wlan0_ch == wlan0_ch_spec:
            if wlan1_ch == wlan1_ch_spec:
                print(colored("\n2G channel list - Passed!","yellow"))
                print(colored("\n5G channel list - Passed!","yellow"))
            else:
                print(colored("\n2G channel list - Passed!","yellow"))
                print(colored("\n5g channel list - Failed!","red"))
                msg = "5G Channel list does not match the spec"
                self.result_message = msg + ',The result is %s' %(wlan1_ch)
                raise Exception (msg)

        else:
            if wlan1_ch == wlan1_ch_spec:
                print(colored("\n2G channel list - Failed!","red"))
                print(colored("\n5G channel list - Passed!","yellow"))
                msg = "2G Channel list does not match the spec"
                self.result_message = msg + ',The result is %s' %(wlan0_ch)
                raise Exception (msg)
            else:
                print(colored("\n2G & 5G channel list - Failed!","red"))
                msg = "2G & 5G Channel list does not match the spec"
                self.result_message = msg + ',The result is %s , %s' %(wlan0_ch, wlan1_ch)
                raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Sample_WIFI_SmartConnect_Enable_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Default Check '''
    
    def runTest(self):
        #Reset the DUT first
        g = Sample_GUI_Test_System_Reset(None)
        g.runTest()
        
        g = Sample_GUI_Test_Disable_Mash(None)
        g.runTest()
        
        global wifi_command,command_802_mode 
        wifi_command = 'smart2g'
        command_802_mode = 'default' #Return to default 802.11 mode
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.Mode802_11()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.get_checklist()
                wifi.send_wpa2_aes()
                wifi.connection_check()        
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break
            
            wifi.get_ssid_2g()

            if 'Pass' in ssid_2g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_2g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s , SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_2g,ch_2g) 
                    wifi.disconnect_2g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
           
        if 'Unable' not in msg:          
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)
        
    def recover(self):
        board.sendcontrol(']')
                
class Sample_WIFI_SmartConnect_Enable_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Default Check '''
    
    def runTest(self):
        global wifi_command 
        wifi_command = 'smart5g'
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.get_checklist()
                wifi.send_wpa2_aes()
                wifi.connection_check()        
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break

            wifi.get_ssid_5g()

            if 'Pass' in ssid_5g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_5g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_5g,ch_5g)
                    wifi.disconnect_5g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
           
        if 'Unable' not in msg:          
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Enable_Modify2G_AES(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Modify Check (WPA2 AES) '''
    
    def main2g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_wpa2_aes()
                wifi.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break
            
            wifi.get_ssid_2g()
            
            if 'Pass' in ssid_2g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_2g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_2g,ch_2g)
                    wifi.disconnect_2g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
            
    def runTest(self):

        #Configure GUI
        #Reset the DUT first
        g = Sample_GUI_Test_System_Reset(None)
        g.runTest()
       
        g = Sample_GUI_Test_Disable_Mash(None)
        g.runTest()

        g = Sample_GUI_Test_WIFI_WPA2(None)
        g.runTest()
        
        


        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-dlinkrouter'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        self.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')
                
class Sample_WIFI_SmartConnect_Enable_Modify5G_AES(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Modify Check (WPA2 AES)'''
   
    def main5g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_wpa2_aes()
                wifi.connection_check()

                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break

            wifi.get_ssid_5g()

            if 'Pass' in ssid_5g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_5g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT , Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 10 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_5g,ch_5g)
                    wifi.disconnect_5g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." %n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
           
    def runTest(self):
        global wifi_command,msg 
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-dlinkrouter'
        wifi_pw_5g = '123456789012345678901234567890123456789012345678901234567890123'        
        wifi_command = 'smart5g'
        
        self.main5g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Sample_WIFI_SmartConnect_Enable_Modify2G_TKIP(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Modify Check (WPA TKIP) '''
   
    def main2g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_wpa_tkip()
                wifi.connection_check()        
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break

            wifi.get_ssid_2g()

            if 'Pass' in ssid_2g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_2g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_2g,ch_2g)
                    wifi.disconnect_2g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
        
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-dlinkrouter'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 's2g_wpatkip'

        self.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Enable_Modify5G_TKIP(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Modify Check (WPA TKIP)'''
   
    def main5g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_wpa_tkip()
                wifi.connection_check()        
            
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 4:
                        raise Exception (msg)
                else:
                    break
                
            wifi.get_ssid_5g()

            if 'Pass' in ssid_5g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_5g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()                    
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_5g,ch_5g)
                    wifi.disconnect_5g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
        
    def runTest(self):
        global wifi_command,msg 
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-dlinkrouter'
        wifi_pw_5g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 's5g_wpatkip'

        self.main5g()
        
        if 'Unable' not in msg:          
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

#Reserved - have issue in DUT
#class Sample_WIFI_SmartConnect_Enable_WPA3_2G(rootfs_boot.RootFSBootTest):
#    '''WIFI 2G Modify Check (WPA3) '''

#    def runTest(self):

        #Configure GUI
#        g = Sample_GUI_Test_WIFI_WPA3(None)
#        g.runTest()

#        global wifi_command
#        global ssid_2g,wifi_pw_2g
#        ssid_2g = 'test-dlinkrouter-wpa3'
#        wifi_pw_2g = '123456789012345678901234567890abcdefghijabcdefghijabcdefghijabc'
#        wifi_command = 'smart2g'

#        h = Sample_WIFI_SmartConnect_Enable_Modify2G(None)
#        h.main2g()
        
#    def recover(self):
#        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Enable_2G_None(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Modify Check (NONE) '''

    def main2g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_none()
                wifi.connection_check()        
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break

            wifi.get_ssid_2g()

            if 'Pass' in ssid_2g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_2g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_2g,ch_2g)
                    wifi.disconnect_2g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
           
    def runTest(self):

        #Configure GUI
        g = Sample_GUI_Test_WIFI_None(None)
        g.runTest()

        global wifi_command,msg
        global ssid_2g
        ssid_2g = 'test-dlinkrouter-none'
        wifi_command = 's2g_none'
        
        self.main2g()
        
        if 'Unable' not in msg:          
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Enable_5G_None(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Modify Check (NONE) '''

    def main5g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_none()
                wifi.connection_check()        
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break

            wifi.get_ssid_5g()

            if 'Pass' in ssid_5g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_5g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Status()
                    msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_5g,ch_5g)
                    wifi.disconnect_5g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 3:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break
        
    def runTest(self):

        global wifi_command,msg
        global ssid_5g
        ssid_5g = 'test-dlinkrouter-none'
        wifi_command = 's5g_none'
        
        self.main5g()
        if 'Unable' not in msg:          
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Sample_WIFI_SmartConnect_Disable_2G_None(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Check (NONE) '''

    def runTest(self):

        #Configure GUI
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_None(rootfs_boot.RootFSBootTest)
        g.runTest()

        global wifi_command,msg
        global ssid_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_command = 's2g_none'
        
        h = Sample_WIFI_SmartConnect_Enable_2G_None(None)
        h.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_None(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Check (NONE) '''    

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_command = 's5g_none'
        
        h = Sample_WIFI_SmartConnect_Enable_5G_None(None)
        h.main5g()
        
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_AES(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Check (WPA2-AES) '''

    def runTest(self):

        #Configure GUI
        g = Sample_GUI_Test_System_Reset(None)
        g.runTest()
        
        g = Sample_GUI_Test_Disable_Mash(None)
        g.runTest()
        
        h = Sample_GUI_Test_SmartConnect_Disable_WIFI_SetupAES(None)
        h.runTest()

        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
                
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_AES(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Check (WAP2-AES) '''    

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
                
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_TKIP(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Check (WPA-TKIP) '''

    def runTest(self):

        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 's2g_wpatkip'
                
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_TKIP(None)
        h.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_TKIP(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Check (WAP2-AES) '''    

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 's5g_wpatkip'
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_TKIP(None)
        h.main5g()
                
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')


class Sample_WIFI_SmartConnect_Disable_2G_Channel1(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 1 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Configure GUI
        g = Sample_GUI_Test_System_Reset(None)
        g.runTest()
        
        k = Sample_GUI_Test_Disable_Mash(None)
        k.runTest()
        
        h = Sample_GUI_Test_SmartConnect_Disable_WIFI_SetupAES(None)
        h.runTest()
        
           

        #Channel 1
        print(colored("\nStarting Channel 1","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)

        #Reset WLAN Client before testing
        wifi = wifi_connect()
        wifi.firstboot()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_1 = ch_2g 
        ch2g_1_msg = msg
        msg_all = '\nch1=' + ch2g_1_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_1 == '1':
            print(colored("\n2G Channel 1 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel2(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 2 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 2
        print(colored("\nStarting Channel 2","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_2 = ch_2g 
        ch2g_2_msg = msg
        msg_all = '\nch2=' + ch2g_2_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_2 == '2':
            print(colored("\n2G Channel 2 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel3(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 3 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 3
        print(colored("\nStarting Channel 3","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_3 = ch_2g 
        ch2g_3_msg = msg
        msg_all = '\nch3=' + ch2g_3_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_3 == '3':
            print(colored("\n2G Channel 3 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel4(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 4 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 4
        print(colored("\nStarting Channel 4","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_4 = ch_2g 
        ch2g_4_msg = msg
        msg_all = '\nch4=' + ch2g_4_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_4 == '4':
            print(colored("\n2G Channel 4 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel5(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 5 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 5
        print(colored("\nStarting Channel 5","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_5 = ch_2g 
        ch2g_5_msg = msg
        msg_all = '\nch5=' + ch2g_5_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_5 == '5':
            print(colored("\n2G Channel 5 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel6(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 6 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 6
        print(colored("\nStarting Channel 6","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_6 = ch_2g 
        ch2g_6_msg = msg
        msg_all = '\nch6=' + ch2g_6_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_6 == '6':
            print(colored("\n2G Channel 6 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel7(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 7 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 7
        print(colored("\nStarting Channel 7","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_7 = ch_2g 
        ch2g_7_msg = msg
        msg_all = '\nch7=' + ch2g_7_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_7 == '7':
            print(colored("\n2G Channel 7 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel8(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 8 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 8
        print(colored("\nStarting Channel 8","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_8 = ch_2g 
        ch2g_8_msg = msg
        msg_all = '\nch8=' + ch2g_8_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_8 == '8':
            print(colored("\n2G Channel 8 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel9(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 9 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 9
        print(colored("\nStarting Channel 9","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_9 = ch_2g 
        ch2g_9_msg = msg
        msg_all = '\nch9=' + ch2g_9_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_9 == '9':
            print(colored("\n2G Channel 9 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel10(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 10 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 10
        print(colored("\nStarting Channel 10","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_10 = ch_2g 
        ch2g_10_msg = msg
        msg_all = '\nch10=' + ch2g_10_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_10 == '10':
            print(colored("\n2G Channel 10 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_2G_Channel11(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Channel 11 Check '''
    
    def runTest(self):
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        
        #Channel 11
        print(colored("\nStarting Channel 11","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_2G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        ch2g_11 = ch_2g 
        ch2g_11_msg = msg
        msg_all = '\nch11=' + ch2g_11_msg
        wifi = wifi_connect()
        wifi.disconnect_2g()

        if ch2g_11 == '11':
            print(colored("\n2G Channel 11 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')


class Sample_WIFI_SmartConnect_Disable_5G_Channel36(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 36 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Configure GUI
        g = Sample_GUI_Test_System_Reset(None)
        g.runTest()
        
        k = Sample_GUI_Test_Disable_Mash(None)
        k.runTest()
        
        h = Sample_GUI_Test_SmartConnect_Disable_WIFI_SetupAES(None)
        h.runTest()       
       
        

        #Channel 36
        print(colored("\nStarting Channel 36","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        
        #Reset WLAN Client before testing
        wifi = wifi_connect()
        wifi.firstboot()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_36 = ch_5g
        ch5g_36_msg = msg
        msg_all = '\nch36=' + ch5g_36_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()
        
        if ch5g_36 == '36':
            print(colored("\n5G Channel 36 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel40(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 40 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 40
        print(colored("\nStarting Channel 40","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_40 = ch_5g
        ch5g_40_msg = msg
        msg_all = '\nch40=' + ch5g_40_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_40 == '40':
            print(colored("\n5G Channel 40 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel44(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 44 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 44
        print(colored("\nStarting Channel 44","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_44 = ch_5g
        ch5g_44_msg = msg
        msg_all = '\nch44=' + ch5g_44_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_44 == '44':
            print(colored("\n5G Channel 44 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel48(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 48 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 48
        print(colored("\nStarting Channel 48","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_48 = ch_5g
        ch5g_48_msg = msg
        msg_all = '\nch48=' + ch5g_48_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_48 == '48':
            print(colored("\n5G Channel 48 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel149(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 149 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 149
        print(colored("\nStarting Channel 149","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_149 = ch_5g
        ch5g_149_msg = msg
        msg_all = '\nch149=' + ch5g_149_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_149 == '149':
            print(colored("\n5G Channel 149 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel153(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 153 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 153
        print(colored("\nStarting Channel 153","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_153 = ch_5g
        ch5g_153_msg = msg
        msg_all = '\nch153=' + ch5g_153_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_153 == '153':
            print(colored("\n5G Channel 153 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel157(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 157 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 157
        print(colored("\nStarting Channel 157","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_157 = ch_5g
        ch5g_157_msg = msg
        msg_all = '\nch157=' + ch5g_157_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_157 == '157':
            print(colored("\n5G Channel 157 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel161(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 161 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 161
        print(colored("\nStarting Channel 161","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_161 = ch_5g
        ch5g_161_msg = msg
        msg_all = '\nch161=' + ch5g_161_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_161 == '161':
            print(colored("\n5G Channel 161 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_5G_Channel165(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Channel 165 Check '''

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        #Channel 165
        print(colored("\nStarting Channel 165","yellow"))
        g = Sample_GUI_Test_SmartConnect_Disable_WIFI_Channel_5G(None)
        g.runTest()
        time.sleep(5)
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        ch5g_165 = ch_5g
        ch5g_165_msg = msg
        msg_all = '\nch165=' + ch5g_165_msg
        wifi = wifi_connect()
        wifi.disconnect_5g()

        if ch5g_165 == '165':
            print(colored("\n5G Channel 165 Test ok","yellow"))
            self.result_message = msg_all
        else:
            print(colored("\nTest Failed , Please check the result","red"))
            self.result_message = msg_all
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Mode802_11bgn_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Mode802_11bgn Check '''

    def mode_11b(self):
        global wifi_command,command_802_mode,msg_b_2g,bit_rate_b_2g
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 's2g_wpatkip'
        command_802_mode = 'b3'
        board.login_elecom()        
        wifi = wifi_connect()
        wifi.Mode802_11()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_TKIP(None)
        h.main2g()
        wifi.get_bit_rate_2g()
        bit_rate_b_2g = bit_rate
        msg_b_2g = msg
        
        if 'Fail' in connection_check:
            bit_rate_b_2g = 'Null'
            msg_b_2g = msg
            wifi.disconnect_2g()
        else:
            wifi.get_bit_rate_2g()
            bit_rate_b_2g = bit_rate
            msg_b_2g = msg
            wifi.disconnect_2g()

    def mode_11g(self):
        global wifi_command,command_802_mode,msg_g_2g,bit_rate_g_2g
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 's2g_wpatkip'
        command_802_mode = 'g2'
        board.login_elecom()        
        wifi = wifi_connect()    
        wifi.Mode802_11()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_TKIP(None)
        h.main2g()
        wifi.get_bit_rate_2g()
        bit_rate_g_2g = bit_rate
        msg_g_2g = msg
        
        if 'Fail' in connection_check:
            bit_rate_g_2g = 'Null'
            msg_g_2g = msg
            wifi.disconnect_2g()
        else:
            wifi.get_bit_rate_2g()
            bit_rate_g_2g = bit_rate
            msg_g_2g = msg
            wifi.disconnect_2g()

    def mode_11n(self):
        global wifi_command,command_802_mode,msg_n_2g,bit_rate_n_2g
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        command_802_mode = 'n1'
        board.login_elecom()        
        wifi = wifi_connect() 
        wifi.Mode802_11()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        wifi.get_bit_rate_2g()
        bit_rate_n_2g = bit_rate
        msg_n_2g = msg
        
        if 'Fail' in connection_check:
            bit_rate_n_2g = 'Null'
            msg_n_2g = msg
            wifi.disconnect_2g()
        else:
            wifi.get_bit_rate_2g()
            bit_rate_n_2g = bit_rate
            msg_n_2g = msg
            wifi.disconnect_2g()

    def runTest(self):
        #Reset WLAN Client before testing
        wifi = wifi_connect()
        wifi.firstboot()
                
        #Reset
        g = Sample_GUI_Test_System_Reset(None)
        g.runTest()
        
        k = Sample_GUI_Test_Disable_Mash(None)
        k.runTest()

        h = Sample_GUI_Test_SmartConnect_Disable_WIFI_SetupAES(None)
        h.runTest()
        
        
        self.mode_11b()
        self.mode_11g()
        self.mode_11n()
        msg_all = '\n802.11b=' + msg_b_2g + ' , Bit Rate=' + bit_rate_b_2g + ' Mbps' + '\n802.11g=' + msg_g_2g + ' , Bit Rate=' + bit_rate_g_2g + ' Mbps' + '\n802.11n=' + msg_n_2g + ' , Bit Rate=' + bit_rate_n_2g + ' Mbps'

        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Mode802_11gn_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Mode802_11gn Check '''

    def runTest(self):
        g = Sample_GUI_Test_WIFI_Mode80211_2G(None)
        g.runTest()
        time.sleep(5)

        h = Sample_WIFI_Mode802_11bgn_2G(None)
        h.mode_11g()
        h.mode_11n()

        msg_all =  '\n802.11g=' + msg_g_2g + ' , Bit Rate=' + bit_rate_g_2g + ' Mbps' + '\n802.11n=' + msg_n_2g + ' , Bit Rate=' + bit_rate_n_2g + ' Mbps'

        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

class Sample_WIFI_Mode802_11n_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Mode802_11gn Check '''

    def runTest(self):
        g = Sample_GUI_Test_WIFI_Mode80211_2G(None)
        g.runTest()
        time.sleep(5)

        h = Sample_WIFI_Mode802_11bgn_2G(None)
        h.mode_11n()

        msg_all = '\n802.11n=' + msg_n_2g + ' , Bit Rate=' + bit_rate_n_2g + ' Mbps'

        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

class Sample_WIFI_Mode802_11anac_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Mode802_11anac Check '''

    def mode_11a(self):
        global wifi_command,command_802_mode,msg_a_5g,bit_rate_a_5g               
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 's5g_wpatkip'
        command_802_mode = 'a4'
        board.login_elecom()        
        wifi = wifi_connect()    
        wifi.Mode802_11()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_TKIP(None)
        h.main5g()
        wifi.get_bit_rate_5g()
        bit_rate_a_5g = bit_rate
        msg_a_5g = msg
        
        if 'Fail' in connection_check:
            bit_rate_a_5g = 'Null'
            msg_a_5g = msg
            wifi.disconnect_5g()
        else:
            wifi.get_bit_rate_5g()
            bit_rate_a_5g = bit_rate
            msg_a_5g = msg
            wifi.disconnect_5g()

    def mode_11n(self):
        global wifi_command,command_802_mode,msg_n_5g,bit_rate_n_5g               
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        command_802_mode = 'n5'
        board.login_elecom()        
        wifi = wifi_connect()    
        wifi.Mode802_11()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        if 'Fail' in connection_check:
            bit_rate_n_5g = 'Null'
            msg_n_5g = msg
            wifi.disconnect_5g()
        else:
            wifi.get_bit_rate_5g()
            bit_rate_n_5g = bit_rate
            msg_n_5g = msg
            wifi.disconnect_5g()

    def mode_11ac(self):
        global wifi_command,command_802_mode,msg_ac_5g,bit_rate_ac_5g               
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        command_802_mode = 'ac6'
        board.login_elecom()        
        wifi = wifi_connect()    
        wifi.Mode802_11()
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        wifi.get_bit_rate_5g()
        bit_rate_ac_5g = bit_rate
        msg_ac_5g = msg

        if 'Fail' in connection_check:
            bit_rate_ac_5g = 'Null'
            msg_ac_5g = msg
            wifi.disconnect_5g()
        else:
            wifi.get_bit_rate_5g()
            bit_rate_ac_5g = bit_rate
            msg_ac_5g = msg
            wifi.disconnect_5g()

    def runTest(self):
        #Reset WLAN Client before testing
        wifi = wifi_connect()
        wifi.firstboot()
            
        #wifi = wifi_connect()
        #wifi.restart()#restart the client when changing the 5G
        self.mode_11a()
        self.mode_11n()
        self.mode_11ac()
    
        msg_all = '\n802.11a=' + msg_a_5g + ' , Bit Rate=' + bit_rate_a_5g + ' Mbps' + '\n802.11n=' + msg_n_5g + ' , Bit Rate=' + bit_rate_n_5g + ' Mbps' + '\n802.11ac=' + msg_ac_5g + ' , Bit Rate=' + bit_rate_ac_5g + ' Mbps'

        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)
     
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Mode802_11nac_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Mode802_11nac Check '''
    
    def runTest(self):
        g = Sample_GUI_Test_WIFI_Mode80211_5G(None)
        g.runTest()
        time.sleep(10)

        h = Sample_WIFI_Mode802_11anac_5G(None)
        h.mode_11n()
        h.mode_11ac()
        
        msg_all = '\n802.11n=' + msg_n_5g + ' , Bit Rate=' + bit_rate_n_5g + ' Mbps' + '\n802.11ac=' + msg_ac_5g + ' , Bit Rate=' + bit_rate_ac_5g + ' Mbps'

        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Mode802_11an_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Mode802_11an Check '''
    
    def runTest(self):
        g = Sample_GUI_Test_WIFI_Mode80211_5G(None)
        g.runTest()
        time.sleep(10)

        h = Sample_WIFI_Mode802_11anac_5G(None)
        h.mode_11a()
        h.mode_11n()
        
        msg_all = '\n802.11a=' + msg_a_5g + ' , Bit Rate=' + bit_rate_a_5g + ' Mbps' + '\n802.11n=' + msg_n_5g + ' , Bit Rate=' + bit_rate_n_5g + ' Mbps' 

        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Mode802_11ac_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Mode802_11ac Check '''
    
    def runTest(self):
        g = Sample_GUI_Test_WIFI_Mode80211_5G(None)
        g.runTest()
        time.sleep(10)

        h = Sample_WIFI_Mode802_11anac_5G(None)
        h.mode_11ac()

        msg_all = '\n802.11ac=' + msg_ac_5g + ' , Bit Rate=' + bit_rate_ac_5g + ' Mbps'
        
        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Mode802_11a_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Mode802_11a Check '''
    
    def runTest(self):
        g = Sample_GUI_Test_WIFI_Mode80211_5G(None)
        #g.runTest()
        time.sleep(10)
    
        h = Sample_WIFI_Mode802_11anac_5G(None)
        h.mode_11n()

        msg_all = '\n802.11a=' + msg_n_5g + ' , Bit Rate=' + bit_rate_n_5g + ' Mbps'
        
        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Mode802_11n_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Mode802_11n Check '''
    
    def runTest(self):
        g = Sample_GUI_Test_WIFI_Mode80211_5G(None)
        g.runTest()
        time.sleep(10) 

        h = Sample_WIFI_Mode802_11anac_5G(None)
        h.mode_11n()

        msg_all = '\n802.11n=' + msg_n_5g + ' , Bit Rate=' + bit_rate_n_5g + ' Mbps'
        
        if 'Unable' not in msg_all:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg_all
            else:
                self.result_message = msg_all
                raise Exception (msg_all)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg_all)

    def recover(self):
        board.sendcontrol(']')

#################################################################
# For Scheudle used
################################################################

class Sample_WIFI_Schedule_on_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Check with Schedule on '''

    def runTest(self):   
        #Reset WLAN Client before testing
        wifi = wifi_connect()
        wifi.firstboot()
        
        #Reset the DUT first
        reset = Sample_GUI_Test_System_Reset(None)
        reset.runTest()
       
        timezone = Sample_GUI_Test_Time_Zone(None)
        timezone.runTest()
        
        k = Sample_GUI_Test_Disable_Mash(None)
        k.runTest()       
        
        on_schedule = Sample_GUI_Test_WIFI_Schedule_on(None)
        on_schedule.runTest()
                
        global wifi_command,msg,command_802_mode
        global ssid_2g,wifi_pw_2g
        command_802_mode = 'default' #Return to default 802.11 mode
        ssid_2g = 'dlink-schedule'
        wifi_pw_2g = '1234567890'
        wifi_command = 'smart2g'
        
        #Return to defualt 802.11 mode
        board.login_elecom()        
        wifi = wifi_connect()
        wifi.Mode802_11()
        
        #Will starting connection
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_Schedule_on_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Check with Schedule on '''    

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'dlink-schedule'
        wifi_pw_5g = '1234567890'
        
        #Reset to default WIFI SSID and Password
        wifi_command = 'default'
        board.login_elecom()
        wifi = wifi_connect()
        wifi.disconnect()
        wifi.send_wpa2_aes()
        
        #Will Starting Connection
        wifi_command = 'smart5g'        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
                
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_out_of_Schedule_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Check with out of Schedule'''

    def main2g(self):
        #It's only used for out of the schedule
        global msg

        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_wpa2_aes()
                wifi.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Pass , Unable to connect to DUT'
                    if i > 2:
                        break
                else:
                    msg = 'WIFI Client can able to connect DUT with out of schedule, Failed'
                    break
            if i > 2:
                break

    def runTest(self):   
        out_schedule = Sample_GUI_Test_WIFI_Out_Of_Schedule(None)
        out_schedule.runTest()
                
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'dlink-schedule'
        wifi_pw_2g = '1234567890'
        wifi_command = 'smart2g'
        
        self.main2g()

        if 'Unable' in msg:
            print(colored("\nPass , WIFI Client cannot able to connect to DUT with out of schedule","yellow"))
            self.result_message = 'Pass , WIFI Client cannot able to connect to DUT with out of schedule'
        else:
            print(colored("\nFail , WIFI Client able to connect to DUT with out of schedule","red"))
            self.result_message = 'Fail , WIFI Client able to connect to DUT with out of schedule'
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_out_of_Schedule_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Check with out of Schedule'''

    def main5g(self):
        #It's only used for out of the schedule
        global msg
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_main()
                wifi.send_wpa2_aes()
                wifi.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Pass , Unable to connect to DUT'
                    if i > 2:
                        break
                else:
                    msg = 'WIFI Client can able to connect DUT with out of schedule, Failed'
                    break
            if i > 2:
                break

    def runTest(self):
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        
        #Reset to default WIFI SSID and Password
        wifi_command = 'default'
        board.login_elecom()
        wifi = wifi_connect()
        wifi.disconnect()
        wifi.send_wpa2_aes()

        ssid_5g = 'dlink-schedule'
        wifi_pw_5g = '1234567890'
        wifi_command = 'smart5g'
       
        self.main5g()

        if 'Unable' in msg:
            print(colored("\nPass , WIFI Client cannot able to connect to DUT with out of schedule","yellow"))
            self.result_message = 'Pass , WIFI Client cannot able to connect to DUT with out of schedule'
        else:
            print(colored("\nFail , WIFI Client able to connect to DUT with out of schedule","red"))   
            self.result_message = 'Fail , WIFI Client able to connect to DUT with out of schedule'
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SC_Disable_Schedule_on_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G SC Disable Check with Schedule on'''

    def runTest(self):       
        on_schedule = Sample_GUI_Test_SC_Disable_WIFI_Schedule_on(None)
        on_schedule.runTest()
                
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g

        ssid_2g = 'dlink-schedule2g'
        wifi_pw_2g = '1234567890'
        wifi_command = 'smart2g'
        
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SC_Disable_Schedule_on_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G SC Disable Check with Schedule on'''

    def runTest(self):                           
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g

        #Reset to default WIFI SSID and Password
        wifi_command = 'default'
        board.login_elecom()
        wifi = wifi_connect()
        wifi.disconnect()
        wifi.send_wpa2_aes()

        ssid_5g = 'dlink-schedule5g'
        wifi_pw_5g = '1234567890'
        wifi_command = 'smart5g'
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SC_Disable_out_of_Schedule_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G SC Disable Check with out of Schedule'''
 
    def runTest(self):   
        #Clear and configure both schedule
        clear_both_schedule = Sample_GUI_Test_SC_Disable_WIFI_Schedule_ClearBoth(None)
        clear_both_schedule.runTest()

        out_schedule = Sample_GUI_Test_SC_Disable_WIFI_out_of_Schedule(None)
        out_schedule.runTest()
                
        global wifi_command,msg
        global ssid_2g,wifi_pw_2g

        #Reset to default WIFI SSID and Password
        wifi_command = 'default'
        board.login_elecom()
        wifi = wifi_connect()
        wifi.disconnect()
        wifi.send_wpa2_aes()

        ssid_2g = 'dlink-schedule2g'
        wifi_pw_2g = '1234567890'
        wifi_command = 'smart2g'
       
        #Connect to wifi
        connect_wifi = Sample_WIFI_out_of_Schedule_2G(None)          
        connect_wifi.main2g()

        if 'Unable' in msg:
            print(colored("\nPass , WIFI Client cannot able to connect to DUT with out of schedule","yellow"))
            self.result_message = 'Pass , WIFI Client cannot able to connect to DUT with out of schedule'
        else:
            print(colored("\nFail , WIFI Client able to connect to DUT with out of schedule","red"))   
            self.result_message = 'Fail , WIFI Client able to connect to DUT with out of schedule'
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SC_Disable_out_of_Schedule_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G SC Disable Check with out of Schedule'''
 
    def runTest(self):                   
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'dlink-schedule5g'
        wifi_pw_5g = '1234567890'
        wifi_command = 'smart5g'
       
        #Connect to wifi
        connect_wifi = Sample_WIFI_out_of_Schedule_5G(None)          
        connect_wifi.main5g()

        if 'Unable' in msg:
            print(colored("\nPass , WIFI Client cannot able to connect to DUT with out of schedule","yellow"))
            self.result_message = 'Pass , WIFI Client cannot able to connect to DUT with out of schedule'
        else:
            print(colored("\nFail , WIFI Client able to connect to DUT with out of schedule","red"))   
            self.result_message = 'Fail , WIFI Client able to connect to DUT with out of schedule'
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

##############################################################
#GuestZone

class Sample_WIFI_GuestZone_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G GuestZone'''
    
    def main2g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_guest()
                wifi.send_wpa2_aes()
                wifi.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break
            
            wifi.get_ssid_2g()
            
            if 'Pass' in ssid_2g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_2g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingDUT_Guest()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Guest()
                    msg = 'ShouldNotPingDUT=%s , PingInternet=%s , ShouldNotBrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_2g,ch_2g)
                    wifi.disconnect_2g()
                    break

            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 10:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break

    def runTest(self):
                
        #Reset the DUT first
        reset = Sample_GUI_Test_System_Reset(None)
        reset.runTest()

        time.sleep(5)

        timezone = Sample_GUI_Test_Time_Zone(None)
        timezone.runTest()
        
        time.sleep(5)
        
        k = Sample_GUI_Test_Disable_Mash(None)
        k.runTest()       
        
        #Configure GuestZone
        guestzone = Sample_GUI_Test_WIFI_GuestZone(None)
        guestzone.runTest()

        global wifi_command,msg,home_network_access
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'guestzone2g'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        #home_network_access = 'on'
        
        #Reset WLAN Client before testing
        wifi = wifi_connect()
        wifi.firstboot()

        self.main2g() 
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)       
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G GuestZone'''
    
    def main5g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_guest()
                wifi.send_wpa2_aes()
                wifi.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break
            
            wifi.get_ssid_5g()
            
            if 'Pass' in ssid_5g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_5g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    
                    global home_network_access,ping_hostpc_result
                    
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    if 'on' in home_network_access:
                        wifi.PingDUT_Guest()
                        wifi.BrowseWebUI_Guest()
                        msg = 'ShouldNotPingDUT=%s , PingInternet=%s , ShouldNotBrowseWEBUI=%s , SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_5g,ch_5g)
                        wifi.disconnect_5g()
                        break

                    elif 'host_network_access_enable' in home_network_access:
                        wifi.PingDUT_Guest()
                        wifi.BrowseWebUI_Guest()
                        wifi.PingHost_PC()
                        wifi.PingHost_PC_Guest()
                        msg = 'ShouldNotPingDUT=%s , PingInternet=%s , ShouldNotBrowseWEBUI=%s, ShouldNotPingHostPC=%s , SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,ping_hostpc_result,iw_ssid_5g,ch_5g) 
                        wifi.disconnect_5g()
                        break

                    elif 'host_network_access_disable' in home_network_access:
                        wifi.PingHost_PC()
                        msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s , PingHostPC=%s , SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,ping_hostpc_result,iw_ssid_5g,ch_5g)
                        wifi.disconnect_5g()
                        break
                   
                    else:
                        wifi.disconnect_5g()
                        break
                                        
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 10:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break

    def runTest(self): 
        global wifi_command,msg,home_network_access
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'guestzone5g'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        home_network_access = 'on'
        self.main5g() 
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)       
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_None_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G GuestZone with None'''
    
    def main2g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_guest()
                wifi.send_none()
                wifi.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break
            
            wifi.get_ssid_2g()
            
            if 'Pass' in ssid_2g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_2g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingDUT_Guest()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Guest()
                    msg = 'ShouldNotPingDUT=%s , PingInternet=%s , ShouldNotBrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_2g,ch_2g)
                    wifi.disconnect_2g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 10:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break

    def runTest(self):        
        #Configure GuestZone
        guestzone = Sample_GUI_Test_WIFI_GuestZone_None(None)
        guestzone.runTest()

        global wifi_command,msg
        global ssid_2g
        ssid_2g = 'guestzone2g'
        wifi_command = 's2g_none'
        self.main2g() 
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)       
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_None_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G GuestZone with None'''
    
    def main5g(self):
        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                board.login_elecom()        
                wifi = wifi_connect()
                wifi.disconnect()
                wifi.ip_routing_guest()
                wifi.send_none()
                wifi.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (msg)
                else:
                    break
            
            wifi.get_ssid_5g()
            
            if 'Pass' in ssid_5g_status:
                print(colored("\nFound SSID from DUT , Continue....","yellow"))
                wifi.get_channel_5g()
                wifi.get_ipaddress()
                if '192.168.2.1' in ipaddress:
                    print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                    m = m +1
                    if m > 10:
                        print(colored("\nUnable to Get IP to DUT in 3 times , Stop the Test","red"))
                        msg = 'Unable to connect to DUT due to failed to get IP'
                        break
                else:
                    wifi.PingDUT()
                    wifi.PingDUT_Status()
                    wifi.PingDUT_Guest()
                    wifi.PingInternet()
                    wifi.PingInternet_Status()
                    wifi.BrowseWebUI()
                    wifi.BrowseWebUI_Guest()
                    msg = 'ShouldNotPingDUT=%s , PingInternet=%s , ShouldNotBrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_5g,ch_5g)
                    wifi.disconnect_5g()
                    break
            else:
                print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                n = n + 1
                if n > 10:                    
                    print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                    msg = 'Unable to connect to DUT'
                    break

    def runTest(self): 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'guestzone5g'
        wifi_command = 's5g_none'
        self.main5g() 
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)       
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_Schedule_on_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G GuestZone with schedule on'''

    def runTest(self):     
        #Configure GuestZone Schedule on
        guestzone_schedule_on = Sample_GUI_Test_WIFI_GuestZone_Schedule_on(None)
        guestzone_schedule_on.runTest()

        global wifi_command,msg,home_network_access
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'guestzone2g'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
        #home_network_access = 'on'

        guestzone = Sample_WIFI_GuestZone_2G(None) 
        guestzone.main2g()

        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)       
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_Schedule_on_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G GuestZone with schedule on'''

    def runTest(self): 
        global wifi_command,msg,home_network_access
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'guestzone5g'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        #home_network_access = 'on'

        guestzone = Sample_WIFI_GuestZone_5G(None) 
        guestzone.main5g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)       
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_out_of_Schedule_2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G GuestZone with out of schedule'''

    def runTest(self):     
        #Configure GuestZone Schedule
        #guestzone_schedule_clear = Sample_GUI_Test_WIFI_GuestZone_Schedule_Clear(None)
        #guestzone_schedule_clear.runTest()
        
        #Reset the DUT first 
        reset = Sample_GUI_Test_System_Reset(None)
        reset.runTest()

        time.sleep(5)

        timezone = Sample_GUI_Test_Time_Zone(None)
        timezone.runTest()
        
        time.sleep(5)
        
        g = Sample_GUI_Test_Disable_Mash(None)
        g.runTest()
        
        #Configure GuestZone
        guestzone = Sample_GUI_Test_WIFI_GuestZone(None)
        guestzone.runTest()
        
        guestzone_out_of_schedule = Sample_GUI_Test_WIFI_GuestZone_Out_Of_Schedule(None)
        guestzone_out_of_schedule.runTest()

        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'guestzone2g'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'

        guestzone = Sample_WIFI_out_of_Schedule_2G(None) 
        guestzone.main2g()

        if 'Unable' in msg:
            print(colored("\nPass , Guest Client cannot able to connect to DUT with out of schedule","yellow"))
        else:
            print(colored("\nFail , Guest Client able to connect to DUT with out of schedule","red"))   
            self.result_message = msg
            raise Exception (msg)          
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_out_of_Schedule_5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G GuestZone with out of schedule'''

    def runTest(self): 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'guestzone5g'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        guestzone = Sample_WIFI_out_of_Schedule_5G(None) 
        guestzone.main5g()

        if 'Unable' in msg:
            print(colored("\nPass , Guest Client cannot able to connect to DUT with out of schedule","yellow"))
        else:
            print(colored("\nFail , Guest Client able to connect to DUT with out of schedule","red"))   
            self.result_message = msg
            raise Exception (msg)          
        
    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_InternetAccessOnly_on(rootfs_boot.RootFSBootTest):
    '''WIFI GuestZone with InternetAccessOnly on'''

    def runTest(self):        
        global wifi_command,msg,home_network_access
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'guestzone5g'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        home_network_access = 'host_network_access_enable'
        
        #Clear schedule
        guestzone_schedule_clear = Sample_GUI_Test_WIFI_GuestZone_Schedule_Clear(None)
        guestzone_schedule_clear.runTest()
        
        guestzone = Sample_WIFI_GuestZone_5G(None) 
        guestzone.main5g()

        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result_guest()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_GuestZone_InternetAccessOnly_off(rootfs_boot.RootFSBootTest):
    '''WIFI GuestZone with InternetAccessOnly off'''

    def runTest(self):        
        global wifi_command,msg,home_network_access
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'guestzone5g'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        home_network_access = 'host_network_access_disable'
        
        #Disable Internet Access Only
        disable_internet_access_only = Sample_GUI_Test_WIFI_GuestZone_InternetAccessOnly(None)
        disable_internet_access_only.runTest()

        guestzone = Sample_WIFI_GuestZone_5G(None) 
        guestzone.main5g()

        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result_guest()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

#--------------------New Function-------------------------------

class Sample_WIFI_SmartConnect_Disable_WPA2_Personal2G(rootfs_boot.RootFSBootTest):
    '''WIFI 2G Check (WPA2-AES) '''

    def runTest(self):

        #Configure GUI
        g = Sample_GUI_Test_System_Reset(None)
        g.runTest()
        
        g = Sample_GUI_Test_Disable_Mash(None)
        g.runTest()
        
        h = Sample_GUI_Test_Disable_WIFI_WPA2_Personal(None)
        h.runTest()

        global wifi_command,msg
        global ssid_2g,wifi_pw_2g
        ssid_2g = 'test-router2g-dsc'
        wifi_pw_2g = '123456789012345678901234567890123456789012345678901234567890123'
        wifi_command = 'smart2g'
                
        h = Sample_WIFI_SmartConnect_Enable_Modify2G_AES(None)
        h.main2g()
        
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

class Sample_WIFI_SmartConnect_Disable_WPA2_Personal5G(rootfs_boot.RootFSBootTest):
    '''WIFI 5G Check (WAP2-AES) '''    

    def runTest(self):
 
        global wifi_command,msg
        global ssid_5g,wifi_pw_5g
        ssid_5g = 'test-router5g-dsc'
        wifi_pw_5g = '111111111122222222223333333333444444444455555555556666666666111'
        wifi_command = 'smart5g'
        
        h = Sample_WIFI_SmartConnect_Enable_Modify5G_AES(None)
        h.main5g()
                
        if 'Unable' not in msg:
            wifi = wifi_connect()
            wifi.wifi_result()
            if 'Pass' in wifi_result:
                self.result_message = msg
            else:
                self.result_message = msg
                raise Exception (msg)
        else: 
            msg = 'Unable to connect to DUT'
            self.result_message = msg
            raise Exception (msg)

    def recover(self):
        board.sendcontrol(']')

#--------------------For Dlink--------------------








