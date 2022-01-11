#--- The Common module is used for wget command ----



import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *


class wget_command:
    
    def get_file(self,url,save_path):

        try:
            print(colored("\nGet file from url","yellow"))
            process = pexpect.spawn("wget %s -O %s" %(url,save_path))
            process.logfile_read = sys.stdout
            process.expect('Saving to:')
            return True              
        except:
            print(colored("\nError to get the file","red")) 
            return False

    
