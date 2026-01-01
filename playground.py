import c3pico as helper
from time import sleep

def test():
    helper.rgb_flash(255,0,0)
    sleep(1)
    helper.rgb_flash(0,255,0)
    sleep(1)
    helper.rgb_flash(0,0,255)
    sleep(1)
