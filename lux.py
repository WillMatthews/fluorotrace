#!/usr/bin/python3
try:
    from pyluxafor import LuxaforFlag
    #Create the file: /etc/udev/rules.d/10-luxafor.rules with the following contents:
    #ACTION=="add", SUBSYSTEM=="usb", ATTRS{idProduct}=="f372", ATTRS{idVendor}=="04d8", MODE:="666"
except Exception:
    print("Pyluxafor not installed... run pip3 install pyluxafor")
    exit()
import time


class Flag:
    def __init__(self):
        try:
            flag = LuxaforFlag()
            flag.off()
        except Exception:
            flag = None
        self.flag = flag
        self.led_list=[i+1 for i in range(6)]


    def busy(self):
        if self.flag is not None:
            self.flag.do_fade_colour(
                        leds=self.led_list,
                        r=100, g=0, b=0,
                        duration=50
                        )


    def ready(self):
        if self.flag is not None:
            self.flag.do_fade_colour(
                        leds=self.led_list,
                        r=0, g=100, b=0,
                        duration=50
                        )


    def run(self):
        if self.flag is not None:
            self.flag.do_fade_colour(
                        leds=self.led_list,
                        r=0, g=0, b=100,
                        duration=50
                        )


    def off(self):
        if self.flag is not None:
            self.flag.off()
