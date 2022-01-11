# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

# History 
# Modify CheckQosScripts
# 2019/2/20 Remark opkgupdate due to not support
import time

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class OpkgList(rootfs_boot.RootFSBootTest):
    '''Opkg list shows installed packages.'''
    def runTest(self):
        board.sendline('\nopkg list-installed | wc -l')
        board.expect('opkg list')
        board.expect('(\d+)\r\n')
        num_pkgs = int(board.match.group(1))
        board.expect(prompt)
        board.sendline('opkg list-installed')
        board.expect(prompt)
        self.result_message = '%s OpenWrt packages are installed.' % num_pkgs
        self.logged['num_installed'] = num_pkgs

class CheckQosScripts(rootfs_boot.RootFSBootTest):
    '''Check default QOS command.'''
    def runTest(self):
        board.sendline('\nuci show fc.config.enabled')
        board.expect("fc.config.enabled='0'")

#class OpkgUpdate(rootfs_boot.RootFSBootTest):
#    '''Opkg is able to update list of packages.'''
#    def runTest(self):
#        board.sendline('\nopkg update && echo "All package lists updated"')
#        board.expect('Updated list of available packages')
#        board.expect('All package lists updated')
#        board.expect(prompt)

