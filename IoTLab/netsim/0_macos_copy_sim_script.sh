#!/bin/zsh

# This script lets us learn about the setuid bit
# It can make a command run with another user credentials
# No matter who is running it

echo "Copying the script"
scp ./raspi_network_sim.sh root@172.16.0.130:/home/norman/

echo "Setting script permissions"
ssh root@172.16.0.130 '\
    chown root:root /home/norman/raspi_network_sim.sh; \
    chmod u+s /home/norman/raspi_network_sim.sh; \
    chmod a+x /home/norman/raspi_network_sim.sh'
