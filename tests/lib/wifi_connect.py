# For Elecom wlan client connect
# --History--


# Command variable of descrption
# "wifi_command" = ctrl security



import re
import rootfs_boot
import time
from devices import board, wan, lan, wlan, prompt
from lib import installers
from devices import power
from termcolor import *

#--------------General Setting--------------
interface_2g = 'apcli0'
interface_5g = 'apclii0'

#DUT configuration
dut_ip = '192.168.2.1'
dut_ip_range = '192.168.2'
internet_ip = '8.8.8.8'

admin ='admin'
password = '2345wert'

#--------------General Setting--------------

class wifi_connect:
    
    def __init_(self,msg,guest_msg,wifi_result):
        
        self.msg = msg
        self.guest_msg = guest_msg
        self.wifi_result = wifi_result
                  
    def connection_check(self):
        #Check wifi connection
        global connection_check
        try:
            i = board.expect(["AndesLedEnhanceOP: Success"], timeout=30)
            if i == 0:
                board.sendline('\n\n\n')
                board.expect(prompt) 
                print(colored("\nConnected the DUT","yellow"))
                connection_check = 'Passed'
            else:
                print(colored("\nConnection Failed","red"))
                connection_check = 'Failed'
                
        except:
            print(colored("\nConnection Failed","red"))
            connection_check = 'Failed'
     
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

    def send_security(self,wifi_command,ssid_2g,wifi_pw_2g,ssid_5g,wifi_pw_5g):
        
        #Send command to station with wpa2_aes
        if 's2g_wpa2aes' in wifi_command:
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
            print(colored("\nConnecting 2G WIFI with WPA2 AES , Please Wait","yellow"))
         
        elif 's5g_wpa2aes' in wifi_command:
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
            print(colored("\nConnecting 5G WIFI with WPA2 AES , Please Wait","yellow"))
        
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
    
        #Send command to station with wpa2_tkip
        elif 's2g_wpatkip' in wifi_command:
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
            print(colored("\nConnecting 2G WIFI with WPA TKIP , Please Wait","yellow"))
         
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
            print(colored("\nConnecting 5G WIFI with WPA TKIP , Please Wait","yellow"))
        
        #Send command to station with wep
        elif 's2g_wep' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=OPEN' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=WEP' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliDefaultKeyID=1' % (interface_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliKey1=%s' % (interface_2g,wifi_pw_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_2g,ssid_2g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_2g))
            board.expect(prompt)
            print(colored("\nConnecting 2G WIFI with WEP , Please Wait","yellow"))
         
        elif 's5g_wep' in wifi_command:
            self.brctl_check()
            board.sendline('iwpriv %s set ApCliEnable=0' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAuthMode=OPEN' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliEncrypType=WEP' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliDefaultKeyID=1' % (interface_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliKey1=%s' % (interface_5g,wifi_pw_5g))
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliSsid=%s' % (interface_5g,ssid_5g))        
            board.expect(prompt)
            board.sendline('iwpriv %s set ApCliAutoConnect=1' % (interface_5g))
            board.expect(prompt)
            print(colored("\nConnecting 5G WIFI with WEP , Please Wait","yellow"))

        #Send command to station with none
        elif 's2g_none' in wifi_command:
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
            print(colored("\nConnecting 2G WIFI with NONE , Please Wait","yellow"))
         
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
            print(colored("\nConnecting 5G WIFI with NONE , Please Wait","yellow"))
           
    def Mode802_11(self,command_802_mode):
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
     
    def get_bit_rate_5g(self):
        global bit_rate        
        n = 0
        while True:
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
    def ip_routing_main(self):
        #Must manual configure to ipaddress / routing before ping test

        board.sendline('\nclear')
        board.expect(prompt)
        board.sendline('ip addr flush dev br-lan')
        board.expect(prompt)
        board.sendline('ip addr add %s.168/24 dev br-lan' %dut_ip_range)
        board.expect(prompt)
        board.sendline('route add default gw %s' %dut_ip)
        board.expect(prompt)
        print(colored("\nConfigure IP routing","yellow"))
    
    def ip_routing_guest(self):
        #Must manual configure to ipaddress / routing
        #ip 192.168.7.1

        board.sendline('\nclear')
        board.expect(prompt)
        board.sendline('ip addr flush dev br-lan')
        board.expect(prompt)
        board.sendline('ip addr add 192.168.7.168/24 dev br-lan')
        board.expect(prompt)
        board.sendline('route add default gw 192.168.7.1')
        board.expect(prompt)
        print(colored("\nConfigure IP routing","yellow"))
    
    def get_ssid_2g(self,ssid_2g):
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
                    print(colored("\nPassed , Wlan client of SSID is the same as DUT","yellow"))
                    break
                else:
                    ssid_2g_status = 'Fail'
                    print(colored("\nFailed , Wlan client is not the same as DUT","red"))
                    break
            except:
                print(colored("\nError command , Retry!!!","red"))

    def get_ssid_5g(self,ssid_5g):
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
                    print(colored("\nPassed , Wlan client of SSID is the same as DUT","yellow"))
                    break
                else:
                    ssid_5g_status = 'Fail'
                    print(colored("\nFailed , Wlan client is not the same as DUT","red"))
                    break
            except:
                print(colored("\nError command , Retry!!!","red"))

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
                        ping_dut_result = 'Passed'
                        print(colored("\nPing DUT OK","yellow"))
                        break
                    else:
                        ping_dut_result = 'Failed'
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
                ping_dut_result = 'Failed'
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
                        ping_internet_result = 'Passed'
                        print(colored("\nPing Internet OK","yellow"))
                        break
                    else:
                        ping_internet_result = 'Failed'
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
                        ping_internet_result = 'Get IP Failed'
                        break

                else:
                    k = k + 1
                    print(colored("\nMore message is not able to read, Retry %s" %k,"yellow"))
                    if k > 10:
                        ping_internet_result = 'Other Fail'
                        break
            except:
                ping_internet_result = 'Failed'
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
                        browse_webui_result = 'Passed'
                        print(colored("\nBrowse WEBUI OK","yellow"))
                        break
                    else:
                        browse_webui_result = 'Failed'
                        print(colored("\nBrowse WEBUI Fail","red"))
                        break

                if i == 1:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Failed'
                        break

                if i == 2:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Failed'
                        break

                if i == 3:
                    j = j + 1
                    print(colored("\nNo route to host , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Failed'
                        break
                else:
                    j = j + 1
                    print(colored("\nError Command , Retry %s" %j,"yellow"))
                    if j > 10:
                        browse_webui_result = 'Failed'
                        break
            except:
                j = j + 1
                browse_webui_result = 'Failed'
                print(colored("\nBrowse WEBUI Fail - Nothing","red"))
                if j > 1:
                    break
  
    def BrowseWebUI_Status(self):
        #if failed , will retry 3 times
        
        n = 0 
        while True:
            if 'Fail' in browse_webui_result:
                n = n + 1
                print(colored("\nBrowse WebUI Status Check Fail , Retry again %s" %n,"yellow"))
                self.BrowseWebUI()
                if n > 1:
                    break
            else:
                print(colored("\nBrowse WebUI Status Check OK","yellow"))
                break

    def restart(self):
        #Restart board
        board.sendline('reboot')
        board.expect('Restarting system',timeout=15)
        board.wait_for_linux()
        
        #Append DNS info 
        board.sendline("echo 'nameserver 8.8.8.8' >> /etc/resolv.conf")
        board.expect(prompt)

    def firstboot(self):        
        #DUT(wlan) reset to default
        print 'DUT will staring to default, please wait!!!'      
        board.sendline('firstboot')
        board.expect('Reset default process is finished')
        board.expect(prompt)
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

        global msg,wifi_result
        self.msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s' % (ping_dut_result,ping_internet_result,browse_webui_result)
        if ping_dut_result == ping_internet_result == browse_webui_result:
            print(colored("\nWIFI Result Pass","yellow"))
            self.wifi_result = 'Pass'
            
        else:
            print(colored("\nWIFI Result Failed with some items","red"))
            print(colored("\n%s" %self.msg,"yellow"))
            self.wifi_result = 'Fail'   

    def guest_wifi_result(self,msg):
        #Check Guest / Multi WIFI Result
        #Should not ping to DUT and Browse webui

        global wifi_result
        
        #Check the behavior
        global ping_dut_result , browse_webui_result

        if 'PingDUT=Failed' in msg:
            msg = msg.replace('PingDUT=Failed','PingDUT=Passed')
            ping_dut_result = 'Passed'   
        else:
            msg = msg.replace('PingDUT=Passed','PingDUT=Failed')
            ping_dut_result = 'Failed'
        
        if 'Fail' in browse_webui_result:
            msg = msg.replace('BrowseWEBUI=Failed','BrowseWEBUI=Passed')
            browse_webui_result = 'Passed'
        else:
            msg = msg.replace('BrowseWEBUI=Passed','BrowseWEBUI=Failed')
            browse_webui_result = 'Failed'
         
        #self.msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s' % (ping_dut_result,ping_internet_result,browse_webui_result)
        self.guest_msg = msg
        if ping_dut_result == ping_internet_result == browse_webui_result:
            print(colored("\nWIFI Result Pass","yellow"))
            self.wifi_result = 'Pass'
            
        else:
            print(colored("\nWIFI Result Failed with some items","red"))
            print(colored("\n%s" %self.guest_msg,"yellow"))
            self.wifi_result = 'Fail'   
     
    def main(self,wifi_command,ssid_2g,wifi_pw_2g,ssid_5g,wifi_pw_5g):
        #2g / 5g  Connection Process

        global msg
        n = 1
        m = 1
        while True:
            for i in range(1,5):
                print(colored("\nSwitch to Wlan Client , Please wait...","yellow"))
                board.login_elecom()        
                self.disconnect()
                self.ip_routing_main()
                self.send_security(wifi_command,ssid_2g,wifi_pw_2g,ssid_5g,wifi_pw_5g)
                self.connection_check()          
                
                if 'Fail' in connection_check:
                    print(colored("\nUnable to connect to DUT ,Try %s" %i ,"red"))
                    self.msg = 'Unable to connect to DUT'
                    if i > 3:
                        raise Exception (self.msg)
                else:
                    break
            
            if ssid_2g != 'none':
                # run to 2g
                self.get_ssid_2g(ssid_2g) 
                if 'Pass' in ssid_2g_status:
                    print(colored("\nFound SSID from DUT , Continue....","yellow"))
                    self.get_channel_2g()
                    self.get_ipaddress()
                    if dut_ip not in ipaddress:
                        print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                        m = m +1
                        if m > 10:
                            print(colored("\nUnable to Get IP to DUT in 10 times , Stop the Test","red"))
                            self.msg = 'Unable to connect to DUT due to failed to get IP'
                            break
                    else:
                        self.PingDUT()
                        self.PingDUT_Status()
                        self.PingInternet()
                        self.PingInternet_Status()
                        self.BrowseWebUI()
                        self.BrowseWebUI_Status()
                        self.msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_2g,ch_2g)
                        self.disconnect_2g()
                        break
                else:
                    print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                    n = n + 1
                    if n > 10:                    
                        print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                        self.msg = 'Unable to connect to DUT'
                        break
            
            # run to 5g 
            else:
                self.get_ssid_5g(ssid_5g) 
                if 'Pass' in ssid_5g_status:
                    print(colored("\nFound SSID from DUT , Continue....","yellow"))
                    self.get_channel_5g()
                    self.get_ipaddress()
                    if dut_ip not in ipaddress:
                        print(colored("\nUnable to Get IP to DUT Try %s" %m ,"red"))
                        m = m +1
                        if m > 10:
                            print(colored("\nUnable to Get IP to DUT in 10 times , Stop the Test","red"))
                            self.msg = 'Unable to connect to DUT due to failed to get IP'
                            break
                    else:
                        self.PingDUT()
                        self.PingDUT_Status()
                        self.PingInternet()
                        self.PingInternet_Status()
                        self.BrowseWebUI()
                        self.BrowseWebUI_Status()
                        self.msg = 'PingDUT=%s , PingInternet=%s , BrowseWEBUI=%s, SSID=%s , CH=%s' % (ping_dut_result,ping_internet_result,browse_webui_result,iw_ssid_5g,ch_5g)
                        self.disconnect_5g()
                        break
                else:
                    print(colored("\nNot Found SSID from DUT , Try %s..." % n,"red"))                 
                    n = n + 1
                    if n > 10:                    
                        print(colored("\nUnable to connect to DUT , STOP the Test","red"))
                        self.msg = 'Unable to connect to DUT'
                        break




