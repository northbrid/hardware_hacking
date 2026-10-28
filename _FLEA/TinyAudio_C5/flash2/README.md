# A bug when reading
This file is here to tell you just one thing. Maybe it will save some time for you. 
`W25Q16CSIG` is a standard flash memory, it should work with `flashrom`, but it did not. 
I kept the device's CPU in RESET and I double-checked all connections, but it did not. 

Then, to make the experiment more effective, I tried to run `flashrom` with `watch`. 
And then it worked. And then I tried it again without `watch`, and it did not. 
The whole thing was fix reproducible: works with `watch`, does not work without `watch`. 

Maybe the watch command somehow influenced the timings of flashrom, I don't know.  
But this is something you should try if you experience the same. 

## Environment to reproduce
- **Laptop**: 16-inch MacBook Pro from November 2023
- **OS**: MacOS Tahoe, I don't remember the exact version
- **Programmer**: CH347 in SPI-VCP mode
- **Flashrom**: flashrom v1.7.0 on Darwin 25.6.0 (arm64)

# Observations
Contains very interesting strings. 

## Radio-related
- list of DAB radio genres:
  - `Rock_Music`
  - `Easy_Listening`
  - `Light_Classical`
  - `Classical_Music`
  - etc...
- frequencies in text format:
  - `7D:192.352MHz`
  - `8A:192.936MHz`
  - etc...
- Exact Nordic channel names:
  - `NORSK POP`
  - `NRK Reg1 OsloVik`
  - `LydenAvNorge` 
- radio status messages:
  - `full scanning`, 
  - `Now tuning`, 
  - etc...

Stations names are a strong evidence the device writes this memory, not only reads, 
as it's very unlikely that the firmware contains the names of exact radio stations. 
But, it's not 100% sure, because it still can be a preset, so it does not start empty.

## Non radio-related
- messages related to other functions: 
  - `Alarm 1`, `Alarm 2`, `Alarm 3`, etc...
  - `Mon-Sun`, `Mon-Fri`, `Mon-Sat`, etc...
  - `Equalizer`
- messages related to the menu system: 
  - `Language` and `Sprache`
  - `Factory Reset` 
  - `Restarting...`
  - `Low Battery`
  - `Good bye!`

## Internal stuff

### In 8-bit format: 
- messages that looks like logs:
  - `Initialize KeyChecker[CH = %x] Procedure at HCM mode`
  - `[TSC_ISR] TSC Interrupt Error`
  - `TUNE SUCCESS`, `TUNE FAIL`
  - `OFDM LOCK`, `OFDM UNLOCK`
- function names in log messages:
  - `proc_nx2Eh_processDLPlus`
  - `nxEh_ack_dab_curAudioDumpDone`
  - `nxEh_cmd_dab_getFreqInfo`
  - `drds_psr_00a_basic_tune`
  - `_setDumpData-EN`
- strings that looks like shell commands:
  - `GetSdkVersion`
  - `SetPlayMode`
  - `SetEqMode`
  - `DAB_GrantSwitching`
  - `RPT_SerfSwitchingInfo`
- other things worth mentioning:
  - `333TDTC2322`

### In 16-bit format: 
- `Nexilion ZNexilion USB2.0 High Speed Device Controller`

## Inferences 
- This is definitively the memory where the firmware resides
- It definitively has readable logs, but maybe interactive shell too
- It should enumerate an USB device (the port is not only for charging)
- It is based on some SDK (maybe their internal SDK, but still)
- There is a thing called `NxUi` and `NxEh`

## Further things to do 
- Search for the CPU-level things (like `TSC_ISR`) to find the SDK
- Search for `drds_psr_00a_basic_tune` to find the radio library