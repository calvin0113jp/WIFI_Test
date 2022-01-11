# Copyright (c) 2020/12/30
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

# History
# The module is used to WAN SWITCH
# Lib = tests/lib/common_switch.py

import re
import rootfs_boot
from devices import board, wan, lan, wlan, prompt
from termcolor import *
from lib.common_switch import *

class Change_WANSwitch_to_DHCP(rootfs_boot.RootFSBootTest):
    '''The common module is used for wan switch'''
    
    def runTest(self):
        vlan_switch = switch_ctrl()
        switch_status = vlan_switch.Connect_switch(pvid='2')
        if switch_status:
            self.result_message = 'Passed , The message is only for environment setup'
        else:
            self.result_message = 'Failed , The message is only for environment setup'
    
    def recover(self):
        board.sendcontrol(']')

class Change_WANSwitch_to_SecurityServer(rootfs_boot.RootFSBootTest):
    '''The common module is used for wan switch'''
    
    def runTest(self):
        vlan_switch = switch_ctrl()
        switch_status = vlan_switch.Connect_switch(pvid='3')
        if switch_status:
            self.result_message = 'Passed , The message is only for environment setup'
        else:
            self.result_message = 'Failed , The message is only for environment setup'
    
    def recover(self):
        board.sendcontrol(']')

class Change_WANSwitch_to_CDRouter(rootfs_boot.RootFSBootTest):
    '''The common module is used for wan switch'''
    
    def runTest(self):
        vlan_switch = switch_ctrl()
        switch_status = vlan_switch.Connect_switch(pvid='4')
        if switch_status:
            self.result_message = 'Passed , The message is only for environment setup'
        else:
            self.result_message = 'Failed , The message is only for environment setup'
    
    def recover(self):
        board.sendcontrol(']')

class Change_WANSwitch_to_PPPoE(rootfs_boot.RootFSBootTest):
    '''The common module is used for wan switch'''
    
    def runTest(self):
        vlan_switch = switch_ctrl()
        switch_status = vlan_switch.Connect_switch(pvid='5')
        if switch_status:
            self.result_message = 'Passed , The message is only for environment setup'
        else:
            self.result_message = 'Failed , The message is only for environment setup'
    
    def recover(self):
        board.sendcontrol(']')
