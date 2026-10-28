# Reading

I can read the contents of the W25Q80JVS with this command if I hold the CPU in reset:  
`flashrom -V -p ch347_spi -c W25Q80RV -r flash.bin`  
I also uploaded the 1Mb dump here as `W25Q80JVS.bin`

# Analysis

Running a `binwalk` does not find anything useful, and the entropy is interesting but not very revealing.
![Entropy](flash/entropy.png)

## Finding pictures

but I had the idea that the welcome picture must be somewhere in this dump, and it must be a bitmap, as JPEG-decoding would be an overkill for this device. And, the whole dump is just 1Mb, so I created a python script that can display the whole thing as an image interpreted in different pixel formats, and it was a success, as it revealed the boot logo at the end of the memory dump.

`RGB565be` is the right pixel format, but padded to 4-byte blocks by duplicating the 2-byte long RGB565be pixels in each block. The logo is 160x240 pixels (so `4x160x240` bytes), and the image area starts at offset `0xCEF40`, so it can be exported with this command:  
`dd if=flash_W25Q80RV.bin of=logo_purple.bin bs=1 skip=$((0xCEF40)) count=$((160*240*4))`

If I convert this area of the memory with [convert.py](./logo/convert.py), I get this:  
![Logo](./logo/logo.png)