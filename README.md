# Welcome to the TRAILDEV!
Here are some tips and tricks for the usage of this device.
## See battery status
Run `batstat`. Ctrl+C to exit.
## Shut down the TRAILDEV
1. Run `sudo shutdown now`.
2. Wait for the green ligit on the Zero to stop flashing.
3. Turn off the switch.
## Program with Nano editor
Run `nano <filename>` to open the Nano editor.
To exit, do `Ctrl+x`, `Y` to save, then `Enter`.
## Use `less` to view the aoutput of a long command.
Pipe a command to `less` to see all of its output.
Use `j`, `k`, `->`, and `<-` to scroll around.
## Flash a microcontroller.
1. TURN OFF THE TRAILDEV.
2. Plug in the Arduino/Pico/whatever.
3. Turn on the TRAILDEV.
4. Go to `~/trail-code` and pick your project.
5. Run `arduino-cli board list` and note which serial port your board is using and its FQBN (if you're using a Pico and it's unknown, try `rp2042:rp2040:rpipico`).
6. Run `arduino-cli compile --fqbn FQBN YourSketchName.ino`
7. Run `arduino-cli upload -p PORT --fqbn FQBN YourSketchName`, replacing PORT, FQBN, and YourSketchName with the appropriate values.
## Reflash a TRAILDEV
1. Plug SD card reader into Pi.
2. `ls /dev | grep sd` to see where it showed up (probably `/dev/sda`.)
3. Run `sudo dd if=/dev/mmcblk0 of=/dev/sda bs=4M status=progress` and wait for it to finish.
4. Run `sudo sync`.
5. Remove the SD card reader.
## Other Info
The TRAILDEV has a better life of 5 to 10 hours, depending on the battery.
The BT key is actually ESC, but becomes backtick/tilde with the FN key.
Holding the FN key also turns the arrows into pageup etc., 
and the Backspace key into Delete.

# Troubleshooting stuff you shouldn't have to do
## Display setup
1. wire the display to spi0-0
2. add to /boot/config.txt: dtoverlay=fbtft,spi0-0,ili9341,reset_pin=25,dc_pin=24,rotate=90
3. add to the end of the line in /boot/cmdline.txt (not on a new line!): fbcon=map:10 fbcon=font:VGA8x8
4. run sudo dpkg-reconfigure console-setup, then choose UTF-8, Guess optimal, Terminus, 6x12 (is there a way to just specify this in the cmdline.txt`?)
## Wifi
Run `sudo nmcli d wifi scan` to get a list of networks, then `sudo nmcli d wifi connect "<SSID>" password "<PASS>"`.
