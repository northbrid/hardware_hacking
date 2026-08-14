#!/bin/zsh -x

# THING LEARNED: It was possible to set IP to 172.16.0.0
# But I get "ping: sendto: Host is down" if I use that

sudo ifconfig en15 172.16.0.10 netmask 255.255.255.0 up
sudo cp dnsmasq.conf /opt/homebrew/etc/dnsmasq.conf
sudo dnsmasq --no-daemon --log-dhcp -d