import neopixel
import ubinascii
from machine import SoftI2C, unique_id
from micropython import const
from machine import Pin, Timer
from network import WLAN, STA_IF, STAT_GOT_IP, STAT_WRONG_PASSWORD, STAT_NO_AP_FOUND
from urequests import get
from time import sleep

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


def button_pressed() -> bool:
    return not button9.value()


def connect_wifi(ssid: str, password: str, timeout: int = 15) -> bool:
    print(f"Connecting to: {ssid}")
    wlan = WLAN(STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(ssid, password)
        while timeout > 0:
            status = wlan.status()
            if status == STAT_GOT_IP:
                return True
            if status == STAT_WRONG_PASSWORD:
                print("ERROR: Wrong password")
                return False
            if status == STAT_NO_AP_FOUND:
                print("ERROR: Network not found")
                return False

            sleep(.25)
            timeout -= 1

    return wlan.isconnected()


def device_id() -> str:
    return ubinascii.hexlify(unique_id()).decode().upper()
