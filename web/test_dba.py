# -*- coding: utf-8 -*-

'''
Test Cases

'''
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import requests
import xpath

#--------------Debug--------------

debug = 0

if debug == 1:
 
    print ('debug=1')
    check_file = r'D:/Projects/###' # webui_check.txt
    save_folder = r'D:/Projects/###' # other used , templatly save files
    fw_file = r'E:/Projects/###'
    fw_upgrade_folder = r'E:/Projects/###'

    # Mapping /home/weblogin.txt
    select = 'debug'
    browser = 'chrome'

    # Mapping /home/device_info.txt 
    dut_ip = '192.168.0.110'
    dut_account = 'admin'
    dut_password = '12345678'

    if 'chrome' in browser:
        browser_select = 'chrome_driver_init'        
    elif 'firefox' in broser:
        browser_select = 'firefox_driver_init'
    elif 'edge' in broser:
        browser_select = 'edge_driver_init'

elif debug == 0:
    print ('debug=0')
    check_file = '/home/webui_check.txt'
    save_folder = '/var/tmp/'
    fw_upgrade_folder = '/home/upgrade/' # mapping to /tftpboot/dba/upgrade
    fw_downgrade_folder = '/home/downgrade/' # mapping to /tftpboot/dba/downgrade
    
    # Read config file
    with open('/home/weblogin.txt','r') as f:
        line = f.readlines()
        read_select = str(line[0]).strip()
        read_browser = str(line[1]).strip()
        select = read_select
        browser = read_browser
        
        if 'chrome' in browser:
            browser_select = 'chrome_driver_init'        
        elif 'firefox' in broser:
            browser_select = 'firefox_driver_init'
        elif 'edge' in broser:
            browser_select = 'edge_driver_init'
    
    with open('/home/device_info.txt','r') as f:
        line1 = f.readlines()
        dut_ip = str(line1[0]).strip()
        dut_account = str(line1[1]).strip()
        dut_password = str(line1[2]).strip()

#---------------------------------

url = 'http://%s/' %dut_ip

# dut_page = url + /admin/ + dut_page
dut_page = ['/admin/status/overview','/admin/system/system','/admin/system/flashops','/admin/network/network/lan','/admin/network/advnetwork','/admin/logout']

@pytest.mark.usefixtures("%s" %browser_select)
class BasicTest:
    print ('Weblogin process')

    def weblogin(self,url):
        count_login = 0
        while True:
            try:
                r = requests.get(url,timeout=15,verify = False)
                self.driver.get(url)
                print('http ' + str(r.status_code))
                if r.status_code == requests.codes.ok:
                    time.sleep(5)
                    print('--- Login ---')
                    self.driver.find_element_by_xpath('//*[@id="luci_password"]').send_keys(dut_password)
                    time.sleep(3)
                    self.driver.find_element_by_xpath('//*[@id="luci_password"]').send_keys(Keys.ENTER)
                    time.sleep(5)
                    if 'Overview' in self.driver.title:
                        print ('Accessed to ' + self.driver.current_url)
                        return True , self.driver.current_url
                        break
            except:
                count_login += 1
                print('Fail to login DUT in ' + str(count_login) ,'times , Will Retry again')
                time.sleep(3)

                if count_login > 10:
                    print('Failed to login DUT > 10 times')
                    return False
                    break

    def weblogin_only(self,url):
        count_login = 0
        while True:
            try:
                r = requests.get(url,timeout=15,verify = False)
                self.driver.get(url)
                print('http ' + str(r.status_code))
                if r.status_code == requests.codes.ok:
                    time.sleep(5)
                    print('--- Login webUI only---')
                    break
            except:
                count_login += 1
                print('Fail to login DUT in ' + str(count_login) ,'times , Will Retry again')
                time.sleep(3)

                if count_login > 10:
                    print('Failed to login DUT > 10 times')
                    return False
                    break

    def Web_Check_Applying(self,apply_time):
        # Detect the web setting is applying or not
    
        try:
            self.driver.find_element_by_xpath(xpath.apply).click() #Apply Setting
            n = 0
            time.sleep(5)    
            self.driver.switch_to_alert().accept()
            print ('Some fields are invalid, cannot save values')
            return False
            
        except:
            print('Waiting For DUT Applying config %s sec' %apply_time)
            for i in range(apply_time):
                time.sleep(1)
            print('Apply config ok')
            return True

    def getFileName(self,dir): 
        #dir = "/tftpboot/filepath"

        for root, dirs, files in os.walk(dir):
            for file in files:
                find_model = os.path.join(root,file)
        fw_name = find_model.replace(dir,"")
        return fw_name

class Test_Nuclias_device_Automation_webUI(BasicTest):
    
    def test_device_webui_login_via_http(self):
        '''This test case is to check for the login function with http'''

        self.weblogin(url)    
    
    def test_device_webui_login_via_https(self):
        '''This test case is to check for the login function with https'''
        
        url = 'https://%s/' %dut_ip
        self.weblogin(url)
    
    def test_device_webUI_Logout(self):
        '''Auto_Nuclias_device_webUI_Logout'''

        get_current_url = self.weblogin(url)
        self.driver.get(get_current_url[1] + dut_page[5])
        time.sleep(3)
        get_username_label = self.driver.find_element_by_xpath(xpath.username_label).text
        assert "User Name" in get_username_label

    def test_device_webUI_Language(self):
        '''Auto_Nuclias_device_webUI_Language'''

        self.weblogin_only(url)
        get_username_label = self.driver.find_element_by_xpath(xpath.username_label).text
        assert "User Name" in get_username_label

    def test_device_webUI_OverviewPage(self):
        '''Auto_Nuclias_device_webUI_Overview page'''

        def iterated_index(list_of_elems, element):
            '''Check value of index'''

            iterated_index_list = []
            for i in range(len(list_of_elems)):
                if list_of_elems[i] == element:
                    iterated_index_list.append(i)
            return iterated_index_list

        get_text_value_result = []
        self.weblogin(url)
        for i in xpath.overview_xpath_list:
            get_text_value = self.driver.find_element_by_xpath(i).text
            get_text_value_result.append(get_text_value)
        print (get_text_value_result)

        # Check null / empty data in list
        check_null_list = iterated_index(get_text_value_result,'null')
        check_empty_list = iterated_index(get_text_value_result,'')
        
        try:
            assert check_null_list == [] and check_empty_list == []
        except:
            for j in check_null_list:
                print ('failed item : ' + xpath.overveiw_column_name[j] + ' = ' + get_text_value_result[j])

            for k in check_empty_list:
                print ('failed item : ' + xpath.overveiw_column_name[k] + ' = ' + get_text_value_result[k])

    def test_device_webUI_IPv6_setting(self):
        '''Check IPv6 Setting'''

        get_current_url = self.weblogin(url)
        self.driver.get(get_current_url[1] + dut_page[4])

        get_ipv6_value = self.driver.find_element_by_xpath(xpath.ipv6_enable).get_attribute("value")
        
        assert "1" == get_ipv6_value

    #-------------------------------------------------------------------------------------------------

    def test_device_webUI_IP_Connection_Type_to_StaticIP(self):
        '''Check connection type to StaticIP'''

        try:
            get_current_url = self.weblogin(url)
            self.driver.get(get_current_url[1] + dut_page[3])
            time.sleep(3)
        
            connection_type = self.driver.find_element_by_xpath(xpath.conn_type).get_attribute("value")
            
            if 'dhcp' in connection_type:
                print ('Now the connection type is DHCP , setup to StaticIP')
                self.driver.find_element_by_xpath(xpath.conn_type_static).click()
                time.sleep(3)
            
                self.driver.find_element_by_xpath(xpath.ipv4_address).clear()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_address).send_keys(xpath.static_ip_value[0])
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_netmask).clear()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_netmask).send_keys(xpath.static_ip_value[1])
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_gateway).clear()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_gateway).send_keys(xpath.static_ip_value[2])
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_dns1).clear()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_dns1).send_keys(xpath.static_ip_value[3])
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_dns2).clear()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_dns2).send_keys(xpath.static_ip_value[4])
                time.sleep(1)
                self.Web_Check_Applying(apply_time=15)
            else:
                 assert False ,"Something Wrong , Unable to configured to StaticIP"                
        except:
            assert False , "Something Wrong , Unable to configured to StaticIP"
                
    def test_device_webUI_IP_Connection_Type_to_DHCP(self):
        '''Check connection type to DHCP'''

        url_static = 'http://%s/' %xpath.static_ip_value[0]
        
        try:
            get_current_url = self.weblogin(url=url_static)
            self.driver.get(get_current_url[1] + dut_page[3])
            time.sleep(3)

            connection_type = self.driver.find_element_by_xpath(xpath.conn_type).get_attribute("value")

            if 'static' in connection_type:
                self.driver.find_element_by_xpath(xpath.conn_type_dhcp).click()
                time.sleep(3)
                self.driver.find_element_by_xpath(xpath.dhcp_dns).click()
                time.sleep(3)
                self.Web_Check_Applying(apply_time=15)
            else:
                assert False , "Something Wrong , Unable to change to DHCP"
        except:
            assert False , "Something Wrong , Unable to change to DHCP"


    def test_device_webUI_IP_Connection_Type_StaticStatus(self):
        '''Check connection type of Static Status'''

        url_static = 'http://%s/' %xpath.static_ip_value[0]

        try:
            self.weblogin(url_static)
            time.sleep(5)
            get_text_value = self.driver.find_element_by_xpath(xpath.overview_Local_Network).text
            print (get_text_value)
            assert "static" in get_text_value
        except:
            assert False

    def test_device_webUI_IP_Connection_Type_DHCPStatus(self):
        '''Check connection type of DHCP Status'''

        try:
            self.weblogin(url)
            time.sleep(5)
            get_text_value = self.driver.find_element_by_xpath(xpath.overview_Local_Network).text
            print (get_text_value)
            assert "dhcp" in get_text_value
        except:
            assert False
    
    #-------------------------------------------------------------------------------------------------
    
    def test_device_webUI_DNS_Name_servers_setting_DHCP(self):
        '''Check DNS Name servers setting - DHCP'''

        try:
            get_current_url = self.weblogin(url)
            self.driver.get(get_current_url[1] + dut_page[3])
            time.sleep(3)
            connection_type = self.driver.find_element_by_xpath(xpath.conn_type).get_attribute("value")            
            
            if 'dhcp' in connection_type:
                if self.driver.find_element_by_xpath(xpath.dhcp_dns).is_selected():
                    self.driver.find_element_by_xpath(xpath.dhcp_dns).click()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).send_keys(xpath.static_ip_value[3])
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).send_keys(xpath.static_ip_value[4])
                    time.sleep(1)                
                    self.Web_Check_Applying(apply_time=15)
                else:
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).send_keys(xpath.static_ip_value[3])
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).send_keys(xpath.static_ip_value[4])
                    time.sleep(1)
                    self.Web_Check_Applying(apply_time=15)                    
            else:
                assert False , "The connection type does not in DHCP mode , Skip test"
        except:
            assert False
    
    def test_device_webUI_DNS_Name_servers_setting_Static(self):
        '''Check DNS Name servers setting - Static'''

        self.test_device_webUI_IP_Connection_Type_to_StaticIP()

    def test_device_webUI_DNS_Name_servers_setting_static_STA(self):
        '''Check DNS Name servers setting - Configured again - STA '''

        url_static = 'http://%s/' %xpath.static_ip_value[0]
        
        try:
            get_current_url = self.weblogin(url=url_static)
            self.driver.get(get_current_url[1] + dut_page[3])
            time.sleep(3)

            connection_type = self.driver.find_element_by_xpath(xpath.conn_type).get_attribute("value")
            if 'static' in connection_type:
                self.driver.find_element_by_xpath(xpath.ipv4_dns1).clear()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_dns1).send_keys(xpath.static_ip_value[3])
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_dns2).clear()
                time.sleep(1)
                self.driver.find_element_by_xpath(xpath.ipv4_dns2).send_keys(xpath.static_ip_value[4])
                time.sleep(1)
                self.Web_Check_Applying(apply_time=15)
            else:
                assert False ,"The connection type does not in Static mode , Skip test"
        except:
            assert False

    def test_device_webUI_DNS_Name_servers_setting_DHCP_STA(self):
        '''Check DNS Name servers setting - Configured DHCP - STA '''

        url_static = 'http://%s/' %xpath.static_ip_value[0]
        
        try:
            get_current_url = self.weblogin(url=url_static)
            self.driver.get(get_current_url[1] + dut_page[3])
            time.sleep(3)

            connection_type = self.driver.find_element_by_xpath(xpath.conn_type).get_attribute("value")

            if 'static' in connection_type:
                print ('Now the connection type is StaticIP , setup to DHCP')
                self.driver.find_element_by_xpath(xpath.conn_type_dhcp).click()
                time.sleep(3)
                if self.driver.find_element_by_xpath(xpath.dhcp_dns).is_selected():
                    self.driver.find_element_by_xpath(xpath.dhcp_dns).click()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).send_keys(xpath.static_ip_value[3])
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).send_keys(xpath.static_ip_value[4])
                    time.sleep(1)                
                    self.Web_Check_Applying(apply_time=15)
                else:
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns1).send_keys(xpath.static_ip_value[3])
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).clear()
                    time.sleep(1)
                    self.driver.find_element_by_xpath(xpath.ipv4_dns2).send_keys(xpath.static_ip_value[4])
                    time.sleep(1)
                    self.Web_Check_Applying(apply_time=15)               
            else:
                assert False , "The connection type does not in Static mode , Skip test"
        except:
            assert False

    def test_device_webUI_DNS_Name_servers_setting_DHCPStatus(self):
        '''Check DNS Name servers setting - DHCPStatus'''

        try:
            self.weblogin(url)
            get_text_value = self.driver.find_element_by_xpath(xpath.overview_Local_Network).text
            time.sleep(5)
            print (get_text_value)
            assert "dhcp" in get_text_value
            assert xpath.static_ip_value[3] in get_text_value
            assert xpath.static_ip_value[4] in get_text_value            
        except:
            assert False

    def test_device_webUI_DNS_Name_servers_setting_StaticStatus(self):
        '''Check DNS Name servers setting - DHCPStatus'''

        url_static = 'http://%s/' %xpath.static_ip_value[0]

        try:
            self.weblogin(url_static)
            get_text_value = self.driver.find_element_by_xpath(xpath.overview_Local_Network).text
            print (get_text_value)
            assert "static" in get_text_value
            assert xpath.static_ip_value[3] in get_text_value
            assert xpath.static_ip_value[4] in get_text_value
        except:
            assert False

    def test_device_webUI_NTP_Server_setting(self):
        '''Check NTP Server setting'''

        try:
            get_current_url = self.weblogin(url)
            self.driver.get(get_current_url[1] + dut_page[1])

            time.sleep(3)
            self.driver.find_element_by_xpath(xpath.ntp_server1).clear()
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.ntp_server1).send_keys(xpath.ntp_server_value[0])
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.ntp_server2).clear()
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.ntp_server2).send_keys(xpath.ntp_server_value[1])
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.ntp_server3).clear()
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.ntp_server3).send_keys(xpath.ntp_server_value[2])
            time.sleep(1)
            self.Web_Check_Applying(apply_time=15)
        except:
            assert False

    def test_device_webUI_NTP_Server_setting_interval_localtime(self):
        '''Check NTP Server setting'''

        def get_local_time():
            # Get local time from PC
            
            now_time = time.localtime()
            localtime_transfer_sec = time.mktime(now_time) # transfer to sec
            return localtime_transfer_sec

        try:
            localtime = get_local_time()
            self.weblogin(url)
            get_dut_localtime = self.driver.find_element_by_xpath(xpath.overview_Local_Time).text
            dut_time = time.strptime(get_dut_localtime,'%a %b %d %H:%M:%S %Y') # transfer to datetime
            dut_time1 = time.mktime(dut_time)

            interval_sec = (dut_time1 - localtime)
            print ("interval_sec = %s" %interval_sec)

            if interval_sec <= 600 and interval_sec >= 0:
                assert True
            elif interval_sec >= -600 and interval_sec <= 0:
                assert True
            else:
                assert False , "Time >=600 sec or <=600 sec"
        except:
            assert False

    def test_device_webUI_Proxy_Setting(self):
        '''Check proxy setting'''
        try:
            get_current_url = self.weblogin(url)
            self.driver.get(get_current_url[1] + dut_page[4])
            time.sleep(3)

            if self.driver.find_element_by_xpath(xpath.proxy_enable).is_selected():
                pass        
            else:
                self.driver.find_element_by_xpath(xpath.proxy_enable).click()

            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.proxy_host).clear()
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.proxy_host).send_keys(xpath.proxy_value[0])
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.proxy_port).clear()
            time.sleep(1)
            self.driver.find_element_by_xpath(xpath.proxy_port).send_keys(xpath.proxy_value[1])
            time.sleep(1)
            self.Web_Check_Applying(apply_time=15)
        except:
            assert False

    def test_device_webUI_Firmware_Upgrade(self):
        '''Check firmware upgrade'''

        def detect_fw_upgrade_finished(upgrade_time):
            # Detect fw upgrade if finished
            
            count_time = 0
            while True:
                try:
                    get_username_label = self.driver.find_element_by_xpath(xpath.username_label).text
                    if 'User Name' in get_username_label:
                        print ('FW upgrade is finished')
                        break
                except:
                    count_time += 1
                    time.sleep(1)
                    if count_time > upgrade_time:
                        break
        try:
            # Get current fw
            fw_upgrade_filename = self.getFileName(dir=fw_upgrade_folder)
            fw_file = fw_upgrade_folder + fw_upgrade_filename

            get_current_url = self.weblogin(url)
            self.driver.get(get_current_url[1] + dut_page[2])
            time.sleep(3)
            self.driver.find_element_by_xpath(xpath.fw_image).send_keys(fw_file)
            time.sleep(5)
            self.driver.find_element_by_xpath(xpath.upgrade).click()
            time.sleep(3)
            
            count_time = 0
            while True:
                try:
                    if 'Flashing' in self.driver.find_element_by_xpath(xpath.upgrade_loading).text:
                        print ('Fw upgrading...please waiting for %s sec' %xpath.upgrade_time)
                        detect_fw_upgrade_finished(upgrade_time=xpath.upgrade_time)
                        break
                except:
                    count_time += 1
                    print ('Waiting for fw upgrade page...')
                    time.sleep(1)
                    if count_time > 60:
                        assert False , "Fw upgrade loading page does not appear more than 60 sec"
                        break
        except:
            assert False

    def test_device_webUI_Firmware_Upgrade_ver(self):
        '''Check fw version in local setting'''

        try:
            # status page
            get_current_url = self.weblogin(url)
            get_status_fw_ver = self.driver.find_element_by_xpath(xpath.overview_Current_Firmware).text
            
            # system fw page
            self.driver.get(get_current_url[1] + dut_page[2])
            time.sleep(3)
            get_local_fw_ver = self.driver.find_element_by_xpath(xpath.current_fw_ver).text
            print ('System FW version = %s' %get_local_fw_ver)
            print ('Status FW version = %s' %get_status_fw_ver)

            fw_upgrade_filename = self.getFileName(dir=fw_upgrade_folder)
            # Compare fw version
            if get_status_fw_ver in fw_upgrade_filename and get_local_fw_ver in fw_upgrade_filename:
                assert True
            else:
                assert False , "FW verison does not the same between status and system page"
        except:
            assert False
    
    def test_device_webUI_Firmware_Upgrade_fake_fw(self):
        '''Check if loading fake fw that will redirect the warnning message'''

        #fw_file = r'C:/Users/PC1/Downloads/fake_image'
        fw_file = '/home/fake_image'

        try:
            get_current_url = self.weblogin(url)
            self.driver.get(get_current_url[1] + dut_page[2])
            time.sleep(3)
            self.driver.find_element_by_xpath(xpath.fw_image).send_keys(fw_file)
            time.sleep(5)
            self.driver.find_element_by_xpath(xpath.upgrade).click()
            time.sleep(3)
            if 'This image is not valid' in self.driver.find_element_by_xpath(xpath.upgrade_warning).text:
                assert True
        except:
            assert False
