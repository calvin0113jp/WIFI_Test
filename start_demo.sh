#!/bin/bash
# History
# The script will launch the Test item and report the result to user mail account

## ---------------------------------------
# 1: Define Test Cases (same as testsuite)
# ----------------------------------------

case1="Test_sample1"
case2="Test_sample2"


## ----------------------------------
# 1: Define variables
# ----------------------------------
EDITOR=vim
PASSWD=/etc/passwd
RED='\033[0;41;30m'
STD='\033[0;0;39m'

#debug path
debug=/home/test/boardfarm/results/debug

#Relpace 
cp -f devices/openwrt_router_default.py devices/openwrt_router.py

# FW file folder
fw_upgrade_s="/tftpboot/upgrade/"
fw_downgrade_s="/tftpboot/downgrade/"
fw_upgrade_d="/tftpboot/dba/upgrade/"
fw_downgrade_d="/tftpboot/dba/downgrade/"

wifi_client="10.0.0.20"

# ----------------------------------
# 2: Defined function
# ----------------------------------

#-----Check IP is vaild or invalid-----
function check_ip() {
	local IP=$1
	VALID_CHECK=$(echo $IP|awk -F. '$1<=255&&$2<=255&&$3<=255&&$4<=255{print "yes"}')
	if echo $IP|grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$" >/dev/null; then
		if [ $VALID_CHECK == "yes" ]; then
			echo "IP $IP  available!"
			return 0
		else
			echo "IP $IP not available!"
			return 1
		fi
	else
		echo "IP format error!"
		return 1
	fi
}

function check_device_ip() {
	local device_IP=$1
	VALID_CHECK=$(echo $device_IP|awk -F. '$1<=255&&$2<=255&&$3<=255&&$4<=255{print "yes"}')
	if echo $device_IP|grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$" >/dev/null; then
		if [ $VALID_CHECK == "yes" ]; then
			echo "IP $device_IP  available!"
			return 0
		else
			echo "IP $device_IP not available!"
			return 1
		fi
	else
		echo "IP format error!"
		return 1
	fi
}

function check_mac() {

	if [ `echo $mac | egrep "^([0-9A-F]{2}:){5}[0-9A-F]{2}$"` ]
	then
		echo "Valid Mac address"
		return 0
    	else
		echo "Invalid Mac address"
		return 1
	fi

	}

# Get fw file name
function fw_file_check(){
	# copy source fw file to destination (mapping docker image file)
	
	cp -f $fw_upgrade_s* $fw_upgrade_d
	get_fwupgrade=`ls $fw_upgrade_s`
	for eachfile_fwupgrade in $get_fwupgrade
	do
		fwupgrade_filename=$eachfile_fwupgrade
	done
}

function upload_fw_file_to_wificlient(){
	# Upload fw file to wifi client

	echo -e "Upload fw file"
	ssh root@$wifi_client -p 22 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 'rm -f /home/upgrade/*'
	scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $fw_upgrade_s$fwupgrade_filename root@$wifi_client:/home/upgrade
	if [ "$?" -eq "0" ];
	then
		echo 'Scp transfter successful'
		return 0
	else
		echo 'Scp transfter failed'
		return 1
	fi
}


#-----Select Model-----

DBA_2820P(){
	modelname="DBA_2820P"
}

DBA_1510P(){
	modelname="DBA_1510P"
}

#---------------------


account(){
	clear
	read -p "Please Input Mail Name!!: " account_mail
	
	while true; do
		read -p "Please Input DUT IP: " dut_ip
		check_device_ip $dut_ip
	[ $? -eq 0 ] && break
	done

	read -p "Please Input Device Account: " dut_account
	read -p "PLease Input Device Password: " dut_password
	read -p "PLease Select DBA Model: 1.2820P 2.1510P: " model
	case $model in
		1) DBA_2820P ;;
		2) DBA_1510P ;;
		*) echo -e "${RED}Error...${STD}" && sleep 1
	esac

	#--------------------------------------------------------	
	#while true; do
	#	read -p "Please Input Device Mac Address: " mac
	#	check_mac $mac
	#[ $? -eq 0 ] && break
	#done
	#---------------------------------------------------------

    echo "=================================================="
	echo "                                                  "
	echo -e "Your mail account is $account_mail@gmail.com"
	echo -e "DUT IP is $dut_ip"  
	echo -e "DUT Account is $dut_account"
	echo -e "DUT Password is $dut_password"
	echo -e "Device Model is $modelname"
	echo -e "                                               "
	echo "=================================================="
	read -p "Please Confirm All Information , or Retun  [y/n]: " response
	while true;
	do
		case $response in
			[Yy]* )
				echo "Confirm OK"

				#Create DeviceIP to file
				rm -f /tftpboot/dba/device_info.txt
				echo "$dut_ip" > /tftpboot/dba/device_info.txt
				echo -e "$dut_account" >> /tftpboot/dba/device_info.txt
				echo -e "$dut_password" >> /tftpboot/dba/device_info.txt
				echo -e "$modelname" >> /tftpboot/dba/device_info.txt
				break;;
			
			[Nn]* ) echo "Please Input Again"
				account
				if [ "$response" == "Y" -o "$response" == "y" ]; then
					break			
				fi
		esac
	done
}


#Prepare the environment
restart_network(){
	echo -e "Connected to ttyusb"
	chmod 666 /dev/ttyUSB0
	echo -e "stopping the network-manage before test"
	/etc/init.d/networking restart
	/etc/init.d/network-manager stop
}

record_user(){
	log_file="/var/log/user_record_boardfarm.txt"
	echo "Time: $now" Username: $account_mail Function:$testcase Status: Sucess>> $log_file
	echo "----------------------------------------------------" >> $log_file
}


pause(){
  read -p "Press [Enter] key to continue..." fackEnterKey
}


########################################Case Start########################################
#1

DKP_Case1(){
	fw_file_check

	if [ -f "$fw_upgrade_s$fwupgrade_filename" ] ; then
			echo "======================FW Information==================================="
			echo "                                                                       "
	    	echo "FWUpgrade file exists. Continue the Testing...                         "
			echo "Upgrade file is $fwupgrade_filename                                    "
			echo "                                                                       "
			echo "======================FW Information==================================="
			
			now=$(date +"%Y%m%d%H%M%S")
			echo -e "Prepare To Starting "
			upload_fw_file_to_wificlient
			upload_status=$?
			if [ "$upload_status" -eq "0" ];
			then
				testcase=$case1
				script -c "./bft --testsuite $testcase -n dba" $debug/dlab_cases_$now.log
				result=/home/test/boardfarm/results/results.html
				result_finish_time=/home/test/boardfarm/results/results_$now.html
				cp -f $result $result_finish_time
				sleep 5
			 
				# Must restart the network after running the test
				restart_network
				echo -e "Sending mail now , please waiting"
				sleep 5
				echo "Please See the Attachment" | mail -s "$testcase" $account_mail@gmail.com -A $result_finish_time
				echo "Mail sent was Done, Please check your email box later"
			else
				echo "======================Warnning======================================"
				echo "                                                                    "
	    		echo "Can not upload fw file , Skipping the Testing                       "
				echo "                                                                    "
				echo "======================Warnning======================================"
			fi
			
	else
			echo "======================Warnning======================================"
			echo "                                                                    "
	    	echo "FWUpgrade file does not exists. Skipping the Testing...             "
			echo "Please Check the firmware files are exists the folder!              "
			echo "                                                                    "
			echo "======================Warnning======================================"
	fi

	record_user
}

DKP_Case2(){
	now=$(date +"%Y%m%d%H%M%S")
	echo -e "Prepare To Starting"
	testcase=$case2
	script -c "./bft --testsuite $testcase -n dba" $debug/dlab_cases_$now.log
	result=/home/test/boardfarm/results/results.html
	result_finish_time=/home/test/boardfarm/results/results_$now.html
	cp -f $result $result_finish_time
	sleep 5
			 
	# Must restart the network after running the test
	restart_network
	echo -e "Sending mail now , please waiting"
	sleep 5
	echo "Please See the Attachment" | mail -s "$testcase" $account_mail@gmail.com -A $result_finish_time
	echo "Mail sent was Done, Please check your email box later"
}

#1
test1(){
	account
	DKP_Case1
	exit 0
}

#2
test2(){
	account
	DKP_Case2
	exit 0
}

#3
test3(){
	account
	DKP_Case2	
	DKP_Case1	
	exit 0
}

test5(){
			
	exit 0
}





# function to display menus
show_menus() {
	clear
	echo "-------------------------------------------------------------------------------------------------"	
	echo "                                 Auto Test- MENU"
	echo "-------------------------------------------------------------------------------------------------"
	echo "1. $case1"
	echo "                                                                                                 "
	echo "2. $case2"
	echo "                                                                                                 "
	echo "3. Run All"
	echo "                                                                                                 "
	echo "7. Exit Menu"
    echo "                                                                                                 "
}

read_options(){
	local choice
	read -p "Enter choice [ 1 - 7] " choice
	case $choice in
		1) test1 ;;
		2) test2 ;;
		3) test3 ;;
		4) test4 ;;
		5) test5 ;;
		6) test6 ;;
		7) exit 0;;
		*) echo -e "${RED}Error...${STD}" && sleep 1
	esac
}
 
# ----------------------------------------------
# 3: Trap CTRL+C, CTRL+Z and quit singles
# ----------------------------------------------
#trap '' SIGINT SIGQUIT SIGTSTP
 
# -----------------------------------
# 4: Main logic - infinite loop
# ------------------------------------
while true
do
	echo -e "[ Environment Check ]"
	while [ 1 ]; do
	ping -c 1 -w 1 8.8.8.8 && result=0 || result =1
	if [ "$result" -eq "0" ]; then
		echo "Internet is ALIVE"
		show_menus
		read_options
			
		break
	fi

	echo "Internet is not Alive , Stopping the test , please check your connection , Retry!!!!!"
	now=$(date)
	log_file="/var/log/user_record_boardfarm.txt"
	echo "Time: $now" Username: $account_mail status: Environment is Not Work >> $log_file
	echo "----------------------------------------------------" >> $log_file
	done
done
