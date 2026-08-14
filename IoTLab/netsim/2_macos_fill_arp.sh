sudo arp -a -d
for i in $(seq 151 254); do ping -c 1 -W 1 172.16.0.$i; done
arp -a