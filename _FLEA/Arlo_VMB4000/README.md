# Arlo Base Station VMB4000

## Briefing

### BOM

| Chip | Function | Notes | 
|------|----------|-------|
| BCM53573B0KRFBG | RF SoC | |
| WinBond W29N01HVSINA | NAND Flash Memory | |
| WinBond W971GG6SB-25 | 1GBIT Parallel DRAM | |
| Genesys GL850S | USB2.0 4-port Hub Controller | |
| FDS6679AZ | P-Channel MOSFET | |
| MAX9271 | 16-Bit GMSL Serializer | Not Sure (4x8 vs 4x6 pins mismatch) |
| RT9048 | Voltage Regulator | |

## 5-pin header 
* `TP5`
* `TP7`
* `TP8`
* `TP9`
* `TP6`

## Serial

The board has a 4-pin header, which is a serial running on baud `115200` with pinout:
* 1: `?`
* 2: `TX` 
* 3: `GND`
* 4: `?`

I was able to capture boot logs and uploaded in here:
* [first](screenlog.first.txt) - After a reset it detected changes (the NVRAM was empty?)
* [second](screenlog.second.txt) - Second time it started up without complaining

# Damages

* I broke the R32 resistor (next to DC14 under the speaker). That resistor is betwen the PIN 7 (ADJ) and 8 (GND) of the RT9048 voltage regulator IC, supposed to form a voltage divider together with the other resistance which is between PIN 6 (Vout) and PIN 7 (ADJ). 
