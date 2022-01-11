#--- The Common module is used for WIFI Sta command ----
# host : 10.0.0.20 - ubuntu 18.04


import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *


class wifista_command:

    def connect_to_device(self,ip='10.0.0.20',user='root',pw='123456',port='22'):
        # Connect to WIFI Sta

        n = 0
        while True:
            try:
                lan.sendline("ssh %s@%s -p %s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" % (user, ip, port))
                i = lan.expect(["yes/no", "assword:", "Last login"], timeout=30)
                if i == 0:
                    lan.sendline("yes")
                    i = self.expect(["Last login", "assword:"])
                    print(colored("\nConnected to WIFI STA","yellow"))
                    break
                if i == 1:
                    lan.sendline(pw)
                    lan.expect(prompt)
                    print(colored("\nConnected to WIFI STA","yellow"))
                    break
            except:
                n += 1
                if n > 10:
                    print(colored("\nUnable to Connect to WIFI STA","red"))
                    msg = "Unable to Connect to WIFI STA"
                    self.result_message = msg
                    raise Exception(msg)
                    break
    
    def device_logout(self):
        # Exit the WIFI Sta 

        try:
            lan.sendline("logout")
            lan.expect("closed",timeout=10)
            lan.expect(prompt,timeout=10)
            lan.sendline("\n\n\n")
            lan.expect(prompt)
            print(colored("\nExit the WIFI STA","yellow"))
        except:
            print(colored("\nUnable to Exit the WIFI STA","red")) 


    def write_dut_info_to_wifista(self,dut_ip,dut_account,dut_password,case,browser):
        # Write dut informaiton to wifista
        # device_info.txt = dut_ip , dut_account , dut_password 
        # weblogin.txt = case , browser

        print(colored("\nWrite DUT info to wifi sta","yellow"))
        lan.sendline('sed -i "1c %s" /home/device_info.txt' %dut_ip)
        lan.expect(prompt)
        lan.sendline('sed -i "2c %s" /home/device_info.txt' %dut_account)
        lan.expect(prompt)
        lan.sendline('sed -i "3c %s" /home/device_info.txt' %dut_password)
        lan.expect(prompt)

        lan.sendline('sed -i "1c %s" /home/weblogin.txt' %case)
        lan.expect(prompt)
        lan.sendline('sed -i "2c %s" /home/weblogin.txt' %browser)
        lan.expect(prompt)

    def wifi_check_ssid_alive(self,ssid):
        # Check ssid is alive in the env
        # command1: nmcli dev wifi

        try:
            lan.sendline("\nnmcli dev wifi |grep -q %s && echo 0 || echo 1" %ssid)
            lan.expect(prompt)
    
            i = lan.expect(["0","1"] ,timeout=30)
            if i == 0:
                print(colored("\nFound SSID","yellow"))
                return True
            elif i == 1:
                print(colored("\nNot Found SSID","yellow"))
                return False
        except:
            print(colored("\nUnable to found the wifi ssid","red")) 
            return False

    def wifi_check_ssid_alive_v2(self,ssid):
        # Check ssid is alive in the env
        # command2: iw dev wlan0 scan |grep "Auto-SSID4-test" && echo 0 || echo 1

        try:
            lan.sendline("\niw dev wlan0 scan |grep -q %s && echo 0 || echo 1" %ssid)
            i = lan.expect(["0","1"] ,timeout=30)
            if i == 0:
                print(colored("\nFound SSID","yellow"))
                return True
            elif i == 1:
                print(colored("\nNot Found SSID","yellow"))
                return False
            lan.expect(prompt,timeout=10)
        except:
            print(colored("\nUnable to found the wifi ssid","red")) 
            return False

    def wifi_connection(self,ssid,password,eap):
        # wifi connection
        # command : nmcli dev wifi connect $ssid password $password ifname wlan0
        # 802.1x / eap : 0=disable 1=enable
        # 802.1x account/password = test/password

        try:
            if eap == 0:
                lan.sendline("\nnmcli dev wifi connect %s password '%s' ifname wlan0" %(ssid,password))
            elif eap == 1: 
                lan.sendline("nmcli connection add \
 type wifi con-name '%s' ifname wlan0 ssid '%s' -- \
 wifi-sec.key-mgmt wpa-eap 802-1x.eap ttls \
 802-1x.phase2-auth mschapv2 802-1x.identity 'test'" %(ssid,ssid))
                lan.expect(prompt,timeout=30)
                
                # Modify profile password
                lan.sendline("nmcli connection modify '%s' 802-1x.password password" %(ssid))
                lan.expect(prompt,timeout=10)
                lan.sendline("nmcli connection up %s" %(ssid)) # wifi profile link up

            i = lan.expect(["successfully"], timeout=30)
            if i == 0:
                print(colored("\nConnected to DUT","yellow"))
                lan.expect(prompt)
                lan.sendline("\nnmcli device status |grep wlan0")
                lan.expect('%s' %ssid)
                lan.expect(prompt,timeout=10)
                print(colored("\nShow status ok","yellow"))
                time.sleep(5)
                return True    
        except:
            print(colored("\nUnable to connected to DUT , Retry","red"))
            return False

    def wifi_connection_with_profile(self,ssid,password):
        # wifi connection with profile
        # used default psk

        try:
            # Add profile
            lan.sendline("nmcli connection add \
 type wifi con-name '%s' ifname wlan0 ssid '%s'" %(ssid,ssid))
            lan.expect(prompt,timeout=10)
            
            # Modify psk  and password
            lan.sendline("nmcli con modify '%s' wifi-sec.key-mgmt wpa-psk" %(ssid))
            lan.expect(prompt,timeout=10)
            lan.sendline("nmcli con modify '%s' wifi-sec.psk %s" %(ssid,password))
            lan.expect(prompt,timeout=10)
            
            # wifi connection up
            lan.sendline("nmcli connection up '%s'" %(ssid))
            lan.expect(prompt,timeout=30)
            i = lan.expect(["successfully"], timeout=30)
            if i == 0:
                print(colored("\nConnected to DUT","yellow"))
                lan.expect(prompt)
                lan.sendline("\nnmcli device status |grep wlan0")
                lan.expect('%s' %ssid)
                lan.expect(prompt,timeout=10)
                print(colored("\nShow status ok","yellow"))
                time.sleep(5)

            return True
        except:
            print(colored("\nUnable to connected to DUT , Retry","red"))
            return False

    def wifi_get_ipaddress(self):
        # Get IP address when connection is created
        
        n = 0
        while True:
            try:
                time.sleep(5)
                lan.sendline('\nip -4 addr show wlan0')
                lan.expect('inet (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
                ipaddress = lan.match.group(1)
                ipaddress = ipaddress.strip()
                lan.expect(prompt)
                print(colored("\nWIFI STA IPAddress is '%s'" % ipaddress,"yellow"))
                return ipaddress
                break
            except:
                n += 1
                print(colored("\nUnable to get WIFI STA of IPAddress , Will try again","red"))
                if n > 3:
                    return False
                    break

    def wifi_connection_disconnect(self,ssid):
        # wifi connection disconnect
        # command : nmcli c delete $ssid

        try:
            lan.sendline("\nnmcli c delete %s" %ssid)
            i = lan.expect(["successfully"], timeout=30)
            if i == 0:
                print(colored("\nDisconnected the SSID","yellow"))
            return True
        except:
            return False

    def wifi_connection_delete_all(self):
        # Delete all wifi connection
        
        print(colored("\nWaiting for WIFI connection for 15 sec" , "yellow"))
        time.sleep(15) # prevent wifi connection sometimes does not working
        
        print(colored("\nDelete all wifi connection" , "yellow"))
        lan.sendline("\nnmcli --pretty --fields UUID,TYPE con show | grep wifi | awk '{print $1}' | while read line; do nmcli con delete uuid  $line; done")
        lan.expect(prompt)
    
    def wifi_interface_reload(self):
        # Down and up the wlan0

        try:
            print(colored("\nRestarting the wifi interface" , "yellow"))
            lan.sendline("\nifconfig wlan0 down")
            lan.expect(prompt)
            lan.sendline("\niwconfig wlan0 txpower off")
            lan.expect(prompt)
            lan.sendline("\niwconfig wlan0 txpower on")
            lan.expect(prompt)
            lan.sendline("\nifconfig wlan0 up")
            lan.expect(prompt)
            return True
        except:
            return False

    def wifi_main_process(self,ssid,password,eap):
        # Wifi main conneciton without create profile
        # Return status , ipaddress

        n = 0
        status = None
        scan_ssid = None
        while True:
            try:
                self.wifi_connection_delete_all()
                self.wifi_check_ssid_alive(ssid)
                connection = self.wifi_connection(ssid,password,eap)
                if connection == True:
                    ipaddress = self.wifi_get_ipaddress()
                    if ipaddress != '':
                        status = 'Passed , Get the WIFI STA IPaddress'
                        scan_ssid = True
                        return status , ipaddress , scan_ssid
                        break
                    else:
                        status = 'Failed , Unale to get the WIFI STA IPaddress'
                        print(colored("\n%s" %status , "yellow"))
                else:
                    n += 1
                    status = 'Failed , WIFI or SSID not found'
                    self.wifi_interface_reload()
                    if n > 3:
                        ipaddress = None
                        return status , ipaddress , scan_ssid
                        break
            except:
                n += 1
                status = 'Failed , WIFI or SSID not found'
                print(colored("\n%s" %status ,"red"))
                self.wifi_connection_disconnect(ssid)
                self.wifi_interface_reload()
                if n > 3:
                    ipaddress = None
                    return status , ipaddress , scan_ssid
                    break

    def wifi_main_process_with_profile(self,ssid,password):
        # Wifi main conneciton with profile (Check broadcast function)
        # step1: connected to ssid
        # step2: delete to ssid
        # Return status , ipaddress , scan_ssid

        n = 0
        status = None
        scan_ssid = None

        while True:
            try:
                self.wifi_connection_delete_all()
                connection = self.wifi_connection_with_profile(ssid,password)
                if connection == True:
                    ipaddress = self.wifi_get_ipaddress()
                    if ipaddress != '':
                        status = 'Passed , Get the WIFI STA IPaddress'
                        self.wifi_connection_delete_all()
                        # scan_ssid = self.wifi_check_ssid_alive_v2(ssid)
                        scan_ssid = True
                        return status , ipaddress , scan_ssid
                        break
                    else:
                        status = 'Failed , Unale to get the WIFI STA IPaddress'
                        print(colored("\n%s" %status , "yellow"))
                else:
                    n += 1
                    status = 'Failed , WIFI or SSID not found'
                    self.wifi_interface_reload()
                    if n > 3:
                        ipaddress = None
                        return status , ipaddress , scan_ssid
                        break
            except:
                n += 1
                status = 'Failed , WIFI or SSID not found'
                print(colored("\n%s" %status ,"red"))
                self.wifi_connection_disconnect(ssid)
                self.wifi_interface_reload()
                if n > 3:
                    ipaddress = None
                    return status , ipaddress , scan_ssid
                    break

            