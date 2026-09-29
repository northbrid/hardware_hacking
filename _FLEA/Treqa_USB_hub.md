# Treqa USB 2.0 High Speed Hub

## BOM

- **x2** MW7211A 
  - 4-port USB 2.0 hub chip
  - Micov Technologies Co., Ltd.

## Fun Fact

It has 7 ports, because it has 2 MW7211A chips connected to each other.
The second USB hub consumes one port of the first USB hub, so only 3 of the 4 ports of the first hub can be exposed.
Then all of the 4 ports of the second hub can be exposed, resulting in `3+4=7` ports available for the user.

## Advice

As a result, the last 4 ports will be slower than the first 3, and it makes a difference which ports do you use. 
It's a good idea to use the ports from 1 to 7, for the devices sorted by speed requirement from the highest to the lowest.
This is something that can be easily communicated with a simple text on the cover, I don't know why they don't do that. 
