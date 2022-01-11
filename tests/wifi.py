#History
#2019/1/29 Add wlan scan function

import re
import rootfs_boot
from devices import board, lan, wlan, prompt
from lib import installers

class WifiScan(rootfs_boot.RootFSBootTest):
    '''Simple test to run a wifi scan'''

    def runTest(self):
        iface_wlan ="wlan0"
        installers.install_iw(lan)

        board.sendline('iwconfig ra0 | grep ESSID:')
        board.expect(prompt)
        info = board.before
        wifiscan_result = re.search(r'elecom.[\w-]+', info)
        wifi_2g_ssid = wifiscan_result.group(0)
        lan.sendline('ifconfig wlan0 up')
        lan.expect(prompt)
        lan.sendline('iw %s scan |grep %s > "/home/wifi_ssid.txt"' % (iface_wlan, wifi_2g_ssid))
        lan.expect(prompt)
        f = open('/home/wifi_ssid.txt','r')
        results = f.read()
        self.result_message = 'Both SSID 2g and 5g shows %s' %(results)


        #iwpriv ra0 set SiteSurvey=1
        #sleep 5
        #iwpriv ra0 get_site_survey ra0
