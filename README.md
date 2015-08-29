#HomeControl

## Server
The Server runs on a Raspberry Pi, which is connected to a 433MHz Transmitter to control the radio sockets and is connected to the buttons of a Senseo Coffee Machine.

### Features
* Accepts every TCP commands sent to the server
* Send LED-Status of coffee machine
* Turn coffee machine on or off
* Do coffee
 * If coffee machine is turned off, it turns it on and wait till it is preheated and sends the coffee-command
* Switch the radio sockets on and off
* Some XBMC stuff I needed, displaying temperature on the NetIO-App and disk space

### Other Info
* [This is the source of the code for switching the sockets](http://pastebin.com/aRipYrZ6)

## Client
The client is only tested on Windows with a Logitech G510s monochrome display

###Features
* Two modes, Senseo and Lights
  * Senseo
    * Show LED-Status of coffee machine
    * Turn on or off
    * Make coffee
    * Shows 'Preheating' info if the coffee machine is turned of and you sent coffee command
    * Shows an awesome two frame animation as coffee is being made
      * There is no difference of the LED flashing, so the animation duration is not exact
    * You should be able to turn off the coffee machine as it is making coffee
    * Button 3 is to switch to Lights-mode
    * Button 4 is to exit the applet
  * Lights
    * Switch on or off one of four radio sockets
    * Pressing a button turns it off
    * Long-pressing a button turns it on
    * Applet is exited after every button-press in Lights-mode (no free button available)