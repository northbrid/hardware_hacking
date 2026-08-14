# IoT Hacking Lab

## Our Own Smart Light Bulb

Our smart light bulb can be controlled both from WiFi and Bluetooth.  
We can use serial port interface to select WiFi network and enter password.  
Anyone in the room can control the light bulb, no bluetooth authentication needed.

### Implementation

We implement it with 3 components:

1. A real Eglo CrossLink 2 light bulb
2. An ESP32 C6 chip that acts as a bridge
3. An ESP32 CYD acting as remote controller

The ESP32 C6 supports both WiFi, BLE and Zigbee. We use it for different purposes:

- To implement our own, intentionally vulnerable BLE communication protocol
- To add WiFi support, with intentionally unsafe storing of the configured password
- To translate our BLE instructions to ZigBee, for actually controlling the light bulb

So, our "bulb" is te ESP32 C6. The Zigbee communication is hidden from the students.  
The ESP32 CYD can change the color through the bridge if the user touches the palette.

### Student Tasks

- Use nRF BLE sniffing (or generated PCAP) to understand what the remote controller does.
- Find the vulnerability: it uses index and value attributes, and the index is not limited.
- Implement a hacking software that will read the indexes coming after 0,1,2 (RGB) bytes.
- Understand the structure of the memory: colors -> WiFi MAC -> password length -> password.
- Find out the WiFi password of our simulated office network.

## Our Own Simulated Office Network

Our office is big, it contains more than 100 devices on the same ethernet network. 

### Implementation

We implement it with 2 components:

1. TPLink WR802N Nano router configured for AP mode
2. A Raspberry PI computer connected to the wired port

In the Raspberry PI we have a script that will create 100 macvlan devices.  
The MAC address gets generated based on the md5sum of the IP address of the interface.  
The router works in AP mode, so all the 100 devices are visible from wireless clients.

### Student Tasks

- Understand the concept of IP and netmask to figure out the IP range to scan
- Implement a python script that will ping all IPs to get the ARP table filled
- Implement another python script that will find the target device based on OUI

## Our Own Simulated Smart Office

We have a website in where our smart office can be controlled (windows, doors) after auth.  
This website also has a "backup" function. That only function does not require password.

### Implementation

We use a Keyestudio Smart Home Kit with custom firmware developed in Arduino Studio.  
After authentication, we store the IP address of the logged-in user.  
Only one user can be logged in, the next login command overwrites it.  

### Student Tasks

- Download the memory image using the `/backup` entry point of the website (from `robots.txt`)
- Write a Python script that can find the hashed password in the memory image
- Use a rainbow table or cracker software to find the actual password
- Enter with the discovered credentials and take over the control.

