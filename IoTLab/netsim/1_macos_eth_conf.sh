#!/bin/zsh -x
sudo ifconfig en15 172.16.0.0 netmask 255.255.255.0 up
sudo cp dnsmasq.conf /opt/homebrew/etc/dnsmasq.conf
sudo dnsmasq --no-daemon --log-dhcp -d

