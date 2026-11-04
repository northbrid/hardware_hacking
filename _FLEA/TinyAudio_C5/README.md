# TinyAudio C5 intro

## From user POV

Found in a Flea Market in Gyor for 500 HUF. Bought it becasue I had no idea what is it, and it's a kind of fun to discover. It gets power from Micro-USB, and instantly turned on when I plugged in. It is a smart audio box for old car radios: it can receive DAB stations or connect to my phone to receive Bluetooth audio, and output the received signal in line-level output, so it can be connected to the AUX of the car. 

It has lots of controls: it has a simple color TFT screen, one rotary encoder for menu navigation, 8 buttons in the top for easy-access radio presets, and 4 function buttons in the front. 

## From hacker POV

The thing that makes it interesting, is that it's a hardware-hacking honeypot: not hacked by anybody else before, and lots of debug interfaces exposed to the PCB with labels. Very exciting target. And, it is very primitive: it's software is on an 1Mb flash chip, which makes it comfortable to analyze, while it still has recognizeable assets (images, etc...)

# From the inside

## Pins

* Headers: 
  * SWD: `3V3`, `GND`, `RST`, `CLK`, `DAT` 
  * JTAG: `3V3`, `GND`, `TCK`, `TDO`, `TDI`, `TMS`
  * USB: `GND`, `5V`, `TX`, `GND` (not matching)
* Known test pins:
  * Audio: `MIC+`, `MIC-`, `SP+`, `SP-`, `LIN`
  * Power: `GND`, `5V`, `3V3`, `MCU_3.3V`
  * ADC: `ADC0`, `ADC1`, `ADC2`
  * USB: `D+`, `D-`, `USBGND`
  * RF: `RFIN`, `RF_1.8V`,
  * AUX: `RO`, `LO`
  * BT: `BT_3.3V`
  * FM: `FM_TX`
* Unknown test pins: 
  * `TEST`
  * `RIN` 

# BOM

## Mainboard

| chip | function |
|------|----------|
| `D-TEK DT666A-SF` | Main CPU | 
| `MTV301` | DAB SoC (???) |
| `25Q16CS1G` | Serial Flash Memory |
| `WinBond W25Q80JVS` | 8 M-BIT SPI Flash Memory |
| `Enspert NX3131` | Auto-industry DAB chip |
| `NAU88C22` | Audio codec with speaker driver | 

### Identifying the main CPU

D-TEK DT666A-SF does not make any sense, this device does not exist on the internet.  
But I guess it's just an extra layer of paint, because I can see an "ARM" text under it.  
And I also faintly see an ST text in a style that is matching with STMicroelectronics's logo. 

It has 64 pins, so have to find an ARM CPU that is available in QFP64 packaging.  
I expect a few options, so let's narrow the search by identifying the connections of the pins.  
I suspect STM32F030, so I will also look at the function of the same PIN of that model. 

#### Power rail connections 

| pin | function | STM32F030 | match? | 
|-----|----------|-----------|--------|
| 12 | `GND` | `VSSA` | [x] |
| 31 | `GND` | `VSS` | [x] |
| 63` | `GND` | `VSS` | [x] |

#### SPI flash connections

| pin | function | STM32F030 | match? |
|-----|----------|-----------|--------|
| 20 | `MOSI` | `PA4` (`SPI1_NSS`) | ? | 
| 21 | `MISO` | `PA5` (`SPI1_SCK`) | ? | 
| 22 | `SCLK` | `PA6` (`SPI1_MISO`) | ? | 

#### Bluetooth module connections

These connections goes through resistors.  
LED1 and LED2 pins of module are pulled up. 

| pin | function | STM32F030 | match? |
|-----|----------|-----------|--------|
| 50 | `UP` | `PA15` | ? |
| 51 | `PIO2` | `PC10` | ? |
| 52 | `POW` | `PC11` | ? | 
| 53 | `DOWN` | `PC12` | ? | 

#### SWD header connections 

| pin | function | STM32F030 | match? |
|-----|----------|-----------|--------|
| 6? 7? | `RST` | `NRST` | ? |
| 46 | `DAT` | `PA13` (`SWDIO`) | [x] |
| 49 | `CLK` | `PA14` (`SWCLK`) | [x] |

#### TP connections

| pin | function | STM32F030 | match? |
|-----|----------|-----------|--------|
| 50 | `TEST` | `PA15` (`RX`) | ? | 
| 49 | `D+` | `PA14` (`SWCLK`) | ? | 


## BT Daughterboard

| chip | function |
|------|----------|
| `CSR 57F68` | Bluetooth transceiver |
| `P24C64C` | i2c Serial EEPROM | 

# Software

| chip | subdirectory | notes |
|------|--------------|-------|
| `W25Q80JVS` | ![flash](flash/) | Contains the boot logo |
| `W25Q16CSIG` | ![flash2](flash2/) | Contains the firmware | 
| `P24C64C` | ![flash3](flash3/) | Contains the BT device name |

For more info, look at the subdirectories. 

