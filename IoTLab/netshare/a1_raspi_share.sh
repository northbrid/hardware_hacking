#!/bin/bash

echo "DOUBLE-CHECKING YOUR ORIGIN"
echo "$SSH_CLIENT"

echo "CONFIGURING ROUTING" 
ip route replace default via 172.16.0.1 dev eth0

echo "CONFIGURING RESOLVE"
echo "nameserver 8.8.8.8" > /etc/resolv.conf

echo "TESTING IP REACHABILITY"
ip route get 8.8.8.8
ping -c1 8.8.8.8

echo "TESTING RESOLVE"
nslookup google.com
