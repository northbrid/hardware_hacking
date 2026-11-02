# HP USB-to-parallel printer adapter

## Sourcing
- Found in: Flea market Tatabanya
- Price was: 2.000 HUF 

## Identification 

### Label on the box
- Q1342-60001
- APFM-0001

### Text on the PCB
- Agilent Technologies
- CART Formatter Cable Rev. B

## BOM

| Chip ID | Function | Notes | 
|---------|----------|-------| 
| `Agi Lent 2AV3-0001` | ASIC | No info available | 
| `ST USB62` | USB Overvoltage Protection | | 
| `ST KF25` | Voltage Regulator | Generates 2.5v from 3.3v |

## Mysteries

### What is Agi Lent? 

This is a connector made by HP, but the company behind it is Agi Lent.  
They were a division inside HP, and became an individual company in 1999.  
Even the CPU in this board is made by Agi Lent, so they must have been significant. 

HP LaserJet 1000 was made in 2001, 2 years after Agi Lent became a separate company.  
So, they continued to cooperate with HP and still made equipments for them.

### The missing 3.3v

When I plugged it into the USB, my computer said `Device Description read failed`  
Because there is nothing on the board to generate 3.3v power which would drive the CPU.

Measuring pointed out that 3.3v is also connected to the following LPT pins:

| Pin Number | Name | Function | 
|------------|------|----------|
| 13 | Select | Active when high, tells the computer that the printer is online |
| 14 | AutoLF | Active when low, enables the auto-LF function of the printer |
| 1 | Strobe | Active when low, I don't know what is the function of it |

This is a strange design, but makes sense.  
It uses the incoming 3.3 to disable unwanted printer functions.  
And it also uses this voltage to power the CPU on the board.  
Not sure why they thought it's better than the USB, but OK. 

But this design comes with a confusing behavior:  
If it's not connected to a powered-on printer, you get the USB error. 

## USB connection

After giving it 3.3v from PSU, the USB enumeration worked: 
- `VID=03f0`, which is Hewlett-Packard
- `PID=0517`, which is LaserJet 1000

In the USB database: https://usb-ids.gowdy.us/read/UD/03f0/0517
