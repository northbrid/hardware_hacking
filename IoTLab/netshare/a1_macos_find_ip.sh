#!/bin/zsh

# SOLUTION 1

# THING LEARNED: that it practically DOES NOT work. 
# It goes IP-by-IP, which is slow for big ranges.

# echo "FINDING ROUTER: IN RANGE 10.0.0.0/8" 
# sudo ifconfig en15 10.0.0.10 netmask 255.0.0.0 up
# sudo arp-scan --interface=en15 --localnet

# echo "FINDING ROUTER: IN RANGE 172.16.0.0/12" 
# sudo ifconfig en15 172.16.0.10 netmask 255.240.0.0 up
# sudo arp-scan --interface=en15 --localnet

# echo "FINDING ROUTER: IN RANGE 192.168.0.0/16" 
# sudo ifconfig en15 192.168.0.10 netmask 255.255.0.0 up
# sudo arp-scan --interface=en15 --localnet

# SOLUTION 2
echo "Disconnect the device, press ENTER and then look for IPs in the output"
read
sudo tcpdump -ni en15 -e 'arp or udp port 67 or udp port 68'
