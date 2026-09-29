# Compaq iPAQ H3600 PDA

I found it in a flea market in Győr for 500 HUF in perfect condition with the German version of Windows Mobile. 

## BOM

Needless to say, that's a lot. But, I will try to note down the main parts. 

| Part Number | Identification |
|-------------|----------------|
| Atmel AT90LS8535 | 8-Bit Microcontroller with 4K/8K Bytes In-System Programmable Flash | 
| LInfinity LX1686CPW | Digital Dimming CCFL Controller IC | 
| MAX685 | Dual-Output DC-DC Converter for CCD and LCD | 
| CY2292F | Three-PLL General-Purpose EPROM Programmable Clock Generator | 
| UDA1341TS | Audio Codec | 
| LCX16244A | Fast CMOS 3.3V 16-Bit Buffer/Line Driver | 

This is just one side of the PCB, but it does not worth removing. 

## Connectors

### Compact Flash (?)

The iPAQ manual claims CompactFlash compatibility, and CF is not only for memory cards, but also for modems.
But, the long connector is not compatible with the connector of my CF memory card, at least not directly. 
The CF card I have has 50 pins in 2 lines, and the iPAQ has 50 pins in one side, so it can be compatible. 

### 12-pin connector

It was surprisingly hard to find anything. Which is surprising, because it was a popular product.  
I only found this pinout, but only 2 votes says it's correct, while 4 votes says it's not.  
https://web.archive.org/web/20260822214631/https://old.pinouts.ru/PortableDevices/ipaq_12p_pinout.shtml

Then I was lucky enough to find a cable in a flea market for 1 bucks that looked like compatible.

It has USB-A in the other end, and if I plug it in, the device gets power but no device gets detected.
Because the power works, I have a reason to believe it's really the thing that I am looking for. 
After disassembling, I can see that the green wire is broken, which can explain why I don't see devices. 
We have a good chance this is really what I was looking for. 

Let\'s compare pinout.ru\'s pinout to what I see inside the connector I got. 

| Pin# | My Connector | Pinouts.ru | Match? | Comments | 
|------|--------------|------------|--------|----------|
| 1 | Connected to USB V+ | AC Adapter power + | OK | Both USB and AC adapter is 5V | 
| 2 | - | AC Adapter power + | Maybe | No need to connect both V+ if they are the same | 
| 3 | - | DTR RS232 | OK | My connector is USB, not serial |
| 4 | USB ground | Ground | OK | |
| 5 | - | CTS RS232 | OK | My connector is USB, not serial |
| 6 | - | RTS RS232 | OK | My connector is USB, not serial |
| 7 | - | TXD RS232 | OK | My connector is USB, not serial |
| 8 | - | RXD RS232	| OK | My connector is USB, not serial |
| 9 | DCD RS232/USB (+5V) | Connected to USB V+ | OK | Carrier detect, should be connected to +5V |
| 10 | - | Ground | Maybe | No need to connect both GND pins if they are the same |
| 11 | USB White | USB Data+ | OK | | 
| 12 | USB Green | USB Data- | OK | | 

I also confirmed with short measuring that the two GND and the two Power+ is the same.  
Moreover, the PIN-12 is exactly where I see the sings that it was soldered earlier.  
So, it's a close-to-100% match. 

After fixing the broken wire, I can see the following device on the bus: `VID=049F,PID=0003`  
We can look it up in the USB database: https://usb-ids.gowdy.us/read/UD/049f/0003  
This is exactly the identifier of the iPAQ PocketPC, so we are good! 

Now we need a software for it. 

#### USB Connection Troubleshooting

When I connect my PocketPC to Windows 10 and it receives the power and data in the same cable, 
I get `Device Descriptor Request Failed` error, I guess because it tries to communicate with it too early. 
Windows does not have the option to re-request the device descriptor, but restarting the OS helps. 
It also helps if I provide power for the device from another source, so it's already running when I plug it in. 

#### Sync Software

WMDC (Windows Mobile Device Center) is the thing I need, and it can be downloaded from here:  
https://www.microsoft.com/en-us/download/details.aspx?id=15&msockid=1810030c5719682c173c125e56df698d

I also had to find drivers, and Microsoft stopped serving them, so I had to use Wayback Machine to get them:
https://web.archive.org/web/20200803205229if_/https://download.microsoft.com/download/0/4/3/0432540e-2d1a-415d-9c9d-a9963e43503e/drvupdate-amd64.exe

WMDC installed successfully and appeared in my start menu, but it did not work. I had to find workaround. Found this: 
- https://junipersys.com/support/article/12162
- https://harvestmaster.com/data/support/WMDC-fixes-for-Win10.msi

After installing the patch, the WMDC starts up, but it does not detect my already connected device. 
Turned out that it only works properly if I connect the device after the WMDC already running.
Together with the USB connection problem mentioned above, it means that a secondary power source is NECESSARY. 

After the connection works, it integrates with my Windows 10 in a surprisingly streamlined way. 
I can even run windows CE app installer on my computer, and it will install the software itself to the PDA. 

#### Software for the PocketPC

- https://ppcplanet.org/archive
  - SimCity 2000 works!
 
  - 
  
