from i2c_devices.eeprom24 import EEPROM24

CHUNK = 256
OUT = "eeprom_24c512.bin"

eeprom = EEPROM24(address=0x50, chip="24C512")
with open(OUT, "wb") as f:
    for offset in range(0, eeprom.size, CHUNK):
        f.write(eeprom.read(offset, min(CHUNK, eeprom.size - offset)))
        print(f"{offset + CHUNK}/{eeprom.size}")
      
eeprom.close()
