#!/bin/zsh -x

# I wanted to demonstrate that I will log in as norman,
# But the script will run as root because of the setuid bit

# I actually learned that it works only with real binaries
# The kernel will run the bash because of #!/bin/bash
# And that binary does not have the setuid flag set. 

# Then, when the shell sees the setuid bit on the script,
# it will print this: ERROR: Run as root (sudo).

# ssh norman@172.16.0.130 "/home/norman/raspi_network_sim.sh"
ssh root@172.16.0.130 "/home/norman/raspi_network_sim.sh"
