#--- The Common module is used for Docker command ----


import re
import os
import sys
import time
import pexpect
from devices import board, wan, lan, wlan, prompt
from termcolor import *


class docker_command:

    def connect_to_device(self,ip='10.0.0.10',user='root',pw='123456',port='22'):
        # Connect to security hole

        n = 0
        while True:
            try:
                lan.sendline("ssh %s@%s -p %s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" % (user, ip, port))
                i = lan.expect(["yes/no", "assword:", "Last login"], timeout=30)
                if i == 0:
                    lan.sendline("yes")
                    i = self.expect(["Last login", "assword:"])
                    print(colored("\nConnected to SecurityHole","yellow"))
                    break
                if i == 1:
                    lan.sendline(pw)
                    lan.expect(prompt)
                    print(colored("\nConnected to SecurityHole","yellow"))
                    break
            except:
                n += 1
                if n > 10:
                    print(colored("\nUnable to Connect to SecurityHole","red"))
                    msg = "Unable to Connect to SecurityHole"
                    self.result_message = msg
                    raise Exception(msg)
                    break
    
    def device_logout(self):
        # Exit the SecurityHole 

        try:
            lan.sendline("exit")
            lan.expect("logout",timeout=10)
            lan.expect(prompt,timeout=10)
            print(colored("\nExit the SecurityHole","yellow"))
            time.sleep(5)
        except:
            print(colored("\nUnable to Exit the SecurityHole","red")) 


    def start_container(self,image):
        # start container with image

        print(colored("\nStarting Container...","yellow"))       
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt) 
        lan.sendline("docker run --net=host --name lan --privileged -it %s /bin/bash" %image)
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)

    def stop_container(self):
        # stop all container

        print(colored("\nStopping Container...","yellow"))
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)

    def check_container(self,image):
        # Check container is alive
        # image = container image name

        print(colored("\nStarting to Check Container status...","yellow"))
        
        lan.sendline("\ndocker inspect %s | grep 'Running'" %image)
        try:
            i = lan.expect(["true", "No such object"], timeout=10)
            if i == 0:
                print(colored("\nContainer is Alive","yellow"))
                container_status = True
            elif i == 1:
                print(colored("\nContainer is Down","yellow"))
                container_status = False
        except:
            print(colored("\nContainer is Down","yellow"))            
            container_status = False
        
        return container_status

    def start_container_dhcpd(self):
        # Start container with dhcpd
        # image:networkboot/dhcpd

        print(colored("\nStarting Container with DHCPD...","yellow"))
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker run --name dhcpd_server -d -it --rm --init --net host -v $(pwd)/data:/data networkboot/dhcpd eth2")
        lan.expect(prompt)
        time.sleep(10)
        print(colored("\nWaiting for server to starting process...","yellow"))
        lan.sendline("\n\n\n")
        lan.expect(prompt)
        
    def start_container_pppoe(self):
        # Start container with pppoe
        # image:pppoe
        # pppoe ip : 10.10.10.100

        print(colored("\nStarting Container with PPPoE...","yellow"))
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker run -d --net=host --name pppoe_server --privileged -it pppoe")
        lan.expect(prompt)
        time.sleep(10)
        print(colored("\nWaiting for server to starting process...","yellow"))
        lan.sendline("docker exec pppoe_server ./start_pppoe.sh")
        lan.expect(prompt)
        lan.sendline("\n\n\n")
        lan.expect(prompt)

    def start_container_proxy(self): 
        # Start container with proxy
        # image:sameersbn/squid
        # proxy ip : 192.168.0.80

        print(colored("\nStarting Container with Proxy Server...","yellow"))
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker run --name squid -d --restart=always --publish 3128:3128 --volume $(pwd)/data/squid.conf:/etc/squid/squid.conf --volume /srv/docker/squid/cache:/var/spool/squid sameersbn/squid:3.5.27-2")
        lan.expect(prompt)
        time.sleep(10)
        print(colored("\nWaiting for server to starting process...","yellow"))
        lan.sendline("\n\n\n")
        lan.expect(prompt)

    def start_container_freeradius(self): 
        # Start container with freeradius
        # image:freeradius
        # proxy ip : 192.168.0.80

        print(colored("\nStarting Container with freeradius Server...","yellow"))
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker run --net=host -d --name freeradius --privileged -it freeradius /bin/bash")
        lan.expect(prompt)
        time.sleep(10)
        lan.sendline("docker exec -it freeradius service freeradius start")
        lan.expect(prompt)
        print(colored("\nWaiting for server to starting process...","yellow"))
        lan.sendline("\n\n\n")
        lan.expect(prompt)


    #-----------------------------vpn-----------------------------

    def get_vpn_client_ipaddress(self):
        # Container is starting , check the vpn connection
        # Get PPP0 ipaddress

        n = 0
        while True:
            try:
                lan.sendline('ifconfig ppp0 |grep inet')
                lan.expect('inet (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
                ipaddress = lan.match.group(1)
                ipaddress = ipaddress.strip()
                lan.expect(prompt)
                print(colored("\nVPN Client IPAddress is '%s'" % ipaddress,"yellow"))
                time.sleep(10)
                return ipaddress
                break
            except:
                n += 1
                print(colored("\nUnable to created the Tunnel, Will try again","red"))
                if n > 3:
                    return False
                    break

    def check_vpn_client_connection(self):
        # Get successful log from vpn_client
        
        n = 0
        while True:
            try:
                lan.sendline("docker logs vpn_client | grep start_pppd")
                time.sleep(5)
                i = lan.expect(["running","No such container"],timeout=10)
                if i == 0:
                    print(colored("\nVPN client connected","yellow"))
                    lan.expect(prompt)
                    ipaddress = self.get_vpn_client_ipaddress()
                    return ipaddress
                elif i == 1:
                    print(colored("\nContainer unable to started","red"))
                    return False                
                break            
            except:
                n += 1
                time.sleep(10)
                print(colored("\nRetrying for VPN Client to connect to DUT...","red"))
                if n > 3:
                    print(colored("\nVPN Client unble to connect to DUT...","red"))
                    return False
                    break

    def start_container_vpn_client(self):
        # Start container with vpn_client(l2tp_over_ipsec)
        # image:ubergarm/l2tp-ipsec-vpn-client
        
        # Setup connection value
        print(colored("\nConfiguring the environment of vpn client...","yellow"))
        lan.sendline("export VPN_SERVER_IPV4='100.100.100.100'")
        lan.expect(prompt)
        lan.sendline("export VPN_PSK='vpntest1234'")
        lan.expect(prompt)
        lan.sendline("export VPN_USERNAME='vpn'")
        lan.expect(prompt)
        lan.sendline("export VPN_PASSWORD='vpntest1234'")
        lan.expect(prompt)
        
        time.sleep(2)

        print(colored("\nStarting Container with VPN_Client...","yellow"))
        lan.sendline("docker stop $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker rm $(docker ps -aq)")
        lan.expect(prompt)
        lan.sendline("docker run --name vpn_client -d --rm -it --privileged --net=host -v /lib/modules:/lib/modules:ro -e VPN_SERVER_IPV4 -e VPN_PSK -e VPN_USERNAME -e VPN_PASSWORD ubergarm/l2tp-ipsec-vpn-client")
        lan.expect(prompt)
        time.sleep(10)
        print(colored("\nWaiting for server to starting process...","yellow"))
        lan.sendline("\n\n\n")
        lan.expect(prompt)
        ipaddress = self.check_vpn_client_connection()
        return ipaddress

    #-----------------------------vpn-----------------------------
