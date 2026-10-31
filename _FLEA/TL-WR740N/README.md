# TP-Link TL-WR740N

## BOM

## Powering

I found just the board in a flea market, without adapter and cover.  
I tried to search for the proper voltage, but I did not find info.  
Tried to drive it with TP-Link's usual 9V, but it did not like it.

I still don't know, but this little stuff is quite flexible about it.  
The CPU runs stable from both **3.3V** or **5V**, so I am powering it from USB. 

## Reading flash

As mentioned in the BOM, It has a GigaDevices **GD25Q32CSIG** flash chip.  
Debian's default flashrom install does not support it, but Mac's homebrew one does.  
But, I did not find way to hold the CPU in reset, so I was not able to read it. 

## Serial port

**J1** on the board looks like serial, and you can identify `PIN3=GND`, `PIN4=VCC`.  
I also guess `PIN2=RX` based on the serial resistor and the pull-up resistor next to it.  
I also made sure with short measuring that it goes to the CPU, so RX should work. 

The remaining `PIN1=TX` leads to `TP28`, and you have `TP18` under the CPU in the back.  
After connecting them, you can communicate on the serial at the usual baud `115200`.

I recorded a boot log and uploaded it as [bootlog1](bootlog1.txt)

### Bootloader

It identifies itself as `U-Boot 1.1.4` and `AP121 (ar9330) U-boot`.  
We have 1 second to type the usual `tpl` word, so we can get a shell.

With the `printenv` command we can see the 2 most important parameters:
- `bootargs`: `console=ttyS0,115200 root=31:02 rootfstype=squashfs init=/sbin/init mtdparts=ar7240-nor0:256k(u-boot),64k(u-boot-env),2752k(rootfs),896k(uImage),64k(NVRAM),64k(ART)`
- `bootcmd`: `bootm 0x9f020000`

Now you may think that getting root access is as simple as `init=/bin/sh`  
But it looks like it ignores both the bootargs and the `bootm` arguments. 

I guess it is hardcoded, so looked at the kernel address with `md 0x9f020000 0x40`.  
I found strings `TP-LINK Technologies`, and `ver. 1.0`, but no bootargs.

Kernel is an `LZMA` image that gets uncompressed, so I don't have too much chance,  
So I went crary and run `md 0x0 0xffffff`, and stopped it only after 185kB of data.  
The resulting dump is here under the name [memdump](memdump.txt)

As part of the U-Boot image, some interesting strings starts at `000247c0`.
- `bootm 0x8022c090` - I don't know what is it, but worth trying
- `The hell do you want flinfo for??` - Specific enough, worth searching for

The bootargs starts at `0x26940`. Changing it is maybe the same as `setenv`, but worth trying.  
The init parameter is at `0x26982`, but U-boot freezes if it does not end with 0, so `0x26980`.  
I changed `/sbin/init` to `/bin/sh` with `mm`, and double-checked with `md 0x26980 0x40`.
```
hornet> mm 0x26980
00026980: 743d2f73 ? 743d2f62
00026984: 62696e2f ? 696e2f73
00026988: 696e6974 ? 68202020
```
`printenv` still displays the same `/sbin/init`, so this is not where U-boot stores variables.  
If I boot it now, the kernel still receives the command line with `init=/sbin/init`.  
Maybe it was just an initial configuration stored in U-boot's binary, parsed when starting up. 

