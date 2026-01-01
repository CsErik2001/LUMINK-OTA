from machine import Pin, SPI
import c3pico as helper
from ssd1680 import SSD1680


def config():
    return SSD1680(
        spi=SPI(
            1,
            baudrate=1000000,
            polarity=0,
            phase=0,
            sck=Pin(helper.SPI_CLK),  # S3-12, C3-1--------
            mosi=Pin(helper.SPI_MOSI),  # S3-11, C3-4-------

        ),
        busy=Pin(6, Pin.IN),  # SAME
        res=Pin(helper.I2C_SCL, Pin.OUT),  # SAME
        dc=Pin(helper.I2C_SDA, Pin.OUT),  # S3-9, C3-8------
        cs=Pin(5, Pin.OUT),  # SAME
    )
