# Ingredients (my stuff)
- TL-WR802N Nano Router
- tp-link UE300C USB-to-ETH adapter
- 3Com Baseline Switch 2952-SFP plus
- Raspberry Pi Model B Rev 2

# NOT: Sharing from MacOS
Theoretically it is possible. I can connect my UE300C to USB, set its IP address with `ifconfig`,  
and then share the connection in Settings -> General -> Sharing -> Internet Sharing setting.  
This setting creates the `bridge100` device, so the Mac becomes a Wireless-to-Ethernet bridge. 

This way I don't need a hub, I can connect my Raspberry Pi directly with the ethernet adapter.  
Also, I can configure the RPi's IP by running `dnsmasq` on Mac, and I can access it's SSH. 

Sounds good, but something did not work properly, and after hours of debugging I gave it up.

# NOT: Sharing from iPhone
I can connect my UE300C to my iPhone too, and the iPhone lets me to configure adapter's IP.  
It does not have a DHCPD service, but if the RPi has static IP, I can communicate with it. 

But, iPhone cannot share the mobile internet connection on this interface at all.

# Using my TL-WR802N
In this mode the RPi talks with my router, closing my laptop out from this picture.  
I still need SSH to communicate with the RPi, so I need a hub in this setup. I use my 3Com switch.  
At least I had the chance to try all 48 ports during `ping`, and I can tell that all port works!

This is the solution that can actually work, but this is also tricky, as TL-WR802N has many modes. 

## NOT: Access Point Mode
Uses the WiFi as listener only, and if a device connects to it, it can access the wired network.  
I used it for our IoTLab purpose: RPi was connected with wire, and ESP32 and my laptop was wireless.  
The RPi can simulate a whole office network and ESP32 is also visible, and laptop can do ARP scan.  
But, for internet sharing, we need something that can connect to a wireless AP. 

## NOT: Client mode
It can connect to a wireless access point, and make it available through the ethernet port.  
It is like connecting the ethernet interface of a device to another device that has a wireless AP.  
But, it is just bridging the wireless and wired together, making it one virtual interface, not two.  
It means no distinct IP for the LAN and WAN, the DHCP must be requested from the wired device,  
and I failed to figure out how can I administer the device if it does not have its own IP. 

## WIPS mode
I fucking don't understand what is it (they say wireless ISP), but it is magic, and provides everything.  
It has one WiFi that it will bridge, and it receives IP from the DHCP behind that WiFi network.  
It also provides it's own second WiFi and I can access the bridged WiFi through it, like a range extender.  
And, it also provides NAT, DHCPD and own subnet through the LAN port that can be the gateway for my RPi. 