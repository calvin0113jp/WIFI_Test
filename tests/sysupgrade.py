# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

# History
# 2019/1/11 Mofify Sysupgrade : 1. Dynamic Capture the FW name and auto count the file size
#                               2. Replace the sysupgrade to sysupgrade_new
# 2019/3/4 Modify the 1./home/fw_image to /tftpboot
#                     2.Support the lan tftp server (Need to install the tftp server first)

import time
import unittest2
import rootfs_boot
import lib
import glob
import os
from os.path import join,getsize
from devices import board, wan, lan, wlan, prompt

class Sysupgrade(rootfs_boot.RootFSBootTest):
    '''Upgrading via sysupgrade works.'''
    def runTest(self):
        super(Sysupgrade, self).runTest()

	#Put the fw file into "/tftpboot/"
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

        board.sendline('touch /etc/config/TEST')
        board.expect('/etc/config/TEST')
        board.expect(prompt)

        board.sendline("cd /tmp")
	board.sendline("tftp -g -r %s %s" %(fw_name,tftp_server_ip))
	board.expect(prompt)
	board.sendline("/sbin/sysupgrade_md5.sh %s /tmp/%s" %(size_result, fw_name))
	board.expect(prompt)
	board.sendline("sysupgrade_new -c /tmp/img_splitaa")
        board.expect("Restarting system", timeout=300)

        #lib.common.wait_for_boot(board)
        #board.boot_linux()
        board.wait_for_linux()

        board.sendline('ls -alh /etc/config/TEST')
        board.expect('/etc/config/TEST\r\n')
        board.expect(prompt)
