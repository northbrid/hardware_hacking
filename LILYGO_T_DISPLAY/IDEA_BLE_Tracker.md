## A triangle of LilyGO display devices for BLE beacon tracking

Just a fun project for learning and utilizing LilyGo T-Display modules in fleet. 

- I will form a triangle of them, so I will have 3 BLE receivers in different positions
- Each receiver will know its own distance and direction from the other receivers
- Each receiver will receive the same packets, but with different singal strengths
- Each module will share its measurements with the other modules  
  So, each module will have 3 signal strength information for all nearby BLE devices
- Each module picks one device from the top 3 closest, and displays its direction

The same mechanism can work with even more devices.

This is a truly cooperative and ad-hoc firmware behavior, so it needs a protocol  
It's not easy to solve multiple access in UART, so let's use I2C, SPI or BLE  
BLE sounds the best option, so I will sketch the protocol for that

1. They will start by displaying a countdown and collecting device names meanwhile  
   While displaying the countdown, all devices will announce their name (`TrackerTriangle`)
2. After the countdown is done, they will perform an automatic round of handshakes
   - They will all advertise the count of other devices they saw with the same name
   - If a device received as many advertisements as many devices it saw, the display turns green
   - All the received advertisements should contain the number that is matching with its own
3. If everything goes well, after the countdowns we will have 3 green screens
4. Now the user needs to adjust positions
   - Each device displays a value like `1/3`, and an arrow initially pointing to random direction
   - This is the "calibrations done", and it starts from 1 because it does need its own position
   - In any device, the user can press the buttons to make the arrow pointing to the target device
   - While the button is pressed, the device will advertise the MAC of its target device
   - If any device sees its own MAC address in advertisement, it will make its screen blinking
   - Result: the user needs to point the arrow to the blinking screen 2 times on each device
5. Each device saw the MAC addresses of the other devices and now they can calculate their purpose  
   - The device with the lowest MAC will display the direction to the closest device  
   - The device with the second lowest MAC will display the direction of the second closest device
   - And so on...
6. Each device will continously collect latest BLE package per MAC, with signal strength information
7. Each device will share its result set with the other devices
8. By knowing the directions to the other devices, 
   and by knowing 3 different RSSI findings for the same set of BLE devices, 
   each devices can calculate the direction to all the nearbly BLE beacons. 
   - The algorithm treats the 3 findings equally, so they all will end up in the same result. 
   - TBD: this is only true if they use the same information for the calculation. I need to make it sure. 
9. Each device will pick the first / second / third nearest device and display its MAC and position arrow. 
   
   
