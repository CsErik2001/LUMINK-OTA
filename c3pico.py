import neopixel
from machine import SoftI2C
from micropython import const
from machine import Pin, Timer
from network import WLAN, STA_IF
from urequests import get
from os import uname
from time import sleep, time

# Pin Assignments

# SPI
SPI_MISO = const(0)
SPI_CLK = const(1)
SPI_MOSI = const(4)

# UART
UART_TX = const(21)
UART_RX = const(20)

# Free
A2 = const(2)
A5 = const(5)
D6 = const(6)

# Battery
VBAT = const(3)  # Make sure to solder the jumper on the back of the board to enable battery voltage measurement.

# I2C
I2C_SDA = const(8)
I2C_SCL = const(10)
i2c = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))

# RGB_LED
RGB = const(7)
_rgb_led = neopixel.NeoPixel(Pin(RGB), 1)


def rgb_led(r: int = 0, g: int = 0, b: int = 0) -> None:
    _rgb_led[0] = (g, r, b)
    _rgb_led.write()


def rgb_flash(r: int = 0, g: int = 0, b: int = 0, period: int = 1000) -> None:
    rgb_led(r, g, b)
    Timer(0).init(mode=Timer.ONE_SHOT, period=period, callback=lambda t: rgb_led(0, 0, 0))


# BUTTON
BUTTON9 = const(9)
button9 = Pin(BUTTON9, Pin.IN, Pin.PULL_UP)


def connect_wifi(ssid: str, password: str, flash: bool = True, hostname: str = "c3-pico") -> None:
    station = WLAN(STA_IF)
    station.active(True)
    station.config(hostname=hostname)
    station.connect(ssid, password)

    print(f'Connecting to {ssid}')
    start_time = time()

    while not station.isconnected() and (time() - start_time) < 10:
        rgb_flash(255, 255, 0, 100) if flash else print("Connecting...")
        sleep(1)

    if station.isconnected():
        rgb_flash(0, 255, 0) if flash else print("Connected")
    else:
        rgb_flash(255, 0, 0) if flash else print("Error")


def get_unique_id() -> str:
    wlan = WLAN(STA_IF)
    wlan.active(True)
    mac = wlan.config('mac')
    unique_id = ''.join(['{:02X}'.format(b) for b in mac])
    return unique_id


def get_device_data() -> dict[str, str]:
    info = uname()
    payload = {
        "uid": get_unique_id(),
        "sysname": info.sysname,
        "nodename": info.nodename,
        "release": info.release,
        "version": info.version,
        "machine": info.machine
    }
    return payload
