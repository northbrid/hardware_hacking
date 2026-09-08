# Terms

## Software Terms

* `REPL` - Read - Eval - Print Loop.
  * The way of how we can provide interactive shell for a script language
 
## Hardware Terms

* `CSI` - Camera Serial Interface
* `DSI` - Display Serial Interface

# OSS

* `FreeRTOS` - Lightweight Real-time OS for handling multitasking. Available through IDF for ESP chips
  * https://github.com/FreeRTOS
* `LVGL` - Light and Versatile Graphics Library - a GUI framework offically supported by Espressif
  * https://github.com/lvgl/lvgl 
* `NodeMCU` - IDF-based FW for ESP chips that provides LUA REPL with components for various pheripherals
  * https://github.com/nodemcu/nodemcu-firmware/tree/dev-esp32
* `UCGLIB` - Graphics library that provides drawing commands, and can control popular TFT screens
  * https://github.com/olikraus/ucglib

# Chips 

* `WS2812` - RGB LED with controller - can be chained serial to form individually addressable strips
* `NFP240H` - A specific 320x240 TFT screen panel with ILI9341 controller
* `ILI9341` - The chip behind many TFT panels, supported by UCGLIB
* `PCF8574` - A chip that translates between 8-bit parallel and I2C

## By Companies

* Espressif
  * SoCs
    * `ESP32` - Popular dual-core SoC with BLE, BT and WiFi by Epressif
    * `ESP32-C3` - Lower power ESP32 with only one core, and no BT (only BLE)
    * `ESP32-C6` - Another instance of the cost-effective C series, but with ZigBee
    * `ESP8266` - Another popular chip by Espressif, but with no BT / BLE, only WiFi
  * Software
    * `EIM` - Espressif Install Manager: Framework for installing Espressif softwares
    * `IDF` - IoT Development Framework: compiler, components and menuconfig for building firmware
* RockChip
  * Manufacturer of Video / AI focused SoCs
* Future Technology Devices Inc. (FTDI)
  * Manufacturer of various interface converter chips
  * Also used as a generic term for USB-to-UART converter
* Nanjing QinHeng Corp. (WCH)
  * A chinese chip manufacturer focusing on interface converters
  * `CH341` (1) - Chip with USB-to-UART, USB-to-SPI, and USB-to-I2C interfaces
  * `CH341` (2) - Popular and cheap EEPROM flasher based on the CH341 chip
* Nordic Semiconductor
  * A chip manufacturer focusing on RF technologies
  * `nRF` - Nordic's wireless-capable MCU family
    * `nRF52840` - nRF chip available as dongle. Can be used for BLE sniffing.
* Texas Instruments (TI)
  * `CC2531` - ZigBee controller MCU
  * Chips other than MCUs
    * Voltage Regulators
    * Audio Amplifiers
* WinBond
  * Flash Memory manufacturer
* MicroChip
  * Manufacturer of industry-focused MCUs with low processing power
  * Their product lines: `PIC16`, `PIC24`, `PIC32`
* CoreChips Shenzhen Microelectronics Co., Ltd.
  * Manufacturer of USB-communicating chips (hubs, etc...)
* Genesys Logic, Inc.
* ITE

# Articles 

* https://www.tavir.hu/cikk-ch341-eeprom-programozo-es-ami-mogotte-van/

