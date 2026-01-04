from time import localtime, ticks_ms

from ble import BLEProvisioner

import requests
from machine import deepsleep

import json
from ota import OTAUpdater
import c3pico as helper
from battery import Battery
from eink_config import config
from settings import Settings


class WeatherStation:

    def __init__(self):
        self.ssd = config()
        self.ssd.init()
        self.settings = Settings()
        self.prov = BLEProvisioner(ble_name="LUMINK")
        self.battery = Battery(helper.VBAT)
        self.ota_updater = OTAUpdater(self.settings.FIRMWARE_URL,
                                      ["battery.py", "c3pico.py", "eink_config.py", "font.py", "main.py",
                                                 "ota.py", "ssd1680.py", "ble.py"], self.settings.BRANCH)
        self.month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.day_names = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
        self.directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    def get_data(self, lat, lon, cnt, units, lang, api_key):
        forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&cnt={cnt}&units={units}&lang={lang}&appid={api_key}'
        current_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&lang={lang}&appid={api_key}'
        forecast = requests.get(forecast_url)
        current = requests.get(current_url)
        if forecast.status_code == 200 and current.status_code == 200:
            return forecast.json(), current.json()
        return None

    def go_to_sleep(self):
        deepsleep(self.settings.DELAY * 1000 - int(ticks_ms()))

    def _load_icon(self, icon_code):
        try:
            return __import__(f'icons._{icon_code}', globals(), locals(), ['icon']).bitmap
        except ImportError:
            return None

    def _moon_phase(self, time_stamp):
        year, month, day = localtime(time_stamp)[:3]

        julian_date = (367 * year - int((7 * (year + int((month + 9) / 12))) / 4) +
                       int((275 * month) / 9) + day + 1721013.5)

        moon_age = ((julian_date - 2451550.1) % 29.53058867) - 1

        if 0 <= moon_age < 1:
            return "new_moon", "New Moon"
        elif 1 <= moon_age < 7:
            return "waxing_crescent", "Waxing Crescent"
        elif 7 <= moon_age < 9:
            return "first_quarter", "First Quarter"
        elif 9 <= moon_age < 14:
            return "waxing_gibbous", "Waxing Gibbous"
        elif 14 <= moon_age < 15:
            return "full_moon", "Full Moon"
        elif 15 <= moon_age < 21:
            return "waning_gibbous", "Waning Gibbous"
        elif 21 <= moon_age < 23:
            return "last_quarter", "Last Quarter"
        elif 23 <= moon_age < 29:
            return "waning_crescent", "Waning Crescent"
        else:
            return "new_moon", "New Moon"

    def display_low_battery(self):
        self.ssd.show_bitmap(self._load_icon("battery"), 100, 16)

    def display_bluetooth(self):
        self.ssd.show_bitmap(self._load_icon("bluetooth"), 100, 16)

    def display_header(self, battery, city, date_time, version):
        self.ssd.draw_rectangle(0, 0, 296, 10, fill=True)
        self.ssd.show_string(f"{version}v, {battery}%", 10, 2, invert=True)
        self.ssd.show_string(f"{city}", 130, 2, invert=True)
        self.ssd.show_string(
            f"{self.month_names[date_time[1] - 1]} {date_time[2]}., {self.day_names[date_time[6]]} {date_time[3]:02}:{date_time[4]:02}",
            185 if len(str(date_time[2])) == 1 else 179, 2, invert=True)

    def display_info(self, current_weather):
        even = localtime(current_weather['dt'] + current_weather['timezone'])[4] % 2 == 0

        self.ssd.show_bitmap(self._load_icon(current_weather['weather'][0]['icon']), 10, 12, multiplier=2)
        self.ssd.show_string(f"{current_weather['weather'][0]['main'][:8]}", 70, 19, multiplier=2)
        self.ssd.show_string(f"{round(current_weather['main']['temp'], 1)}°", 70, 43, multiplier=2)

        moon_icon, moon_state = self._moon_phase(current_weather['dt'] + current_weather['timezone'])

        if even:
            self.ssd.show_bitmap(self._load_icon(moon_icon), 246, 18)
            self.ssd.show_string(
                f"{localtime(current_weather['sys']['sunrise'] + current_weather['timezone'])[3]:02}:{localtime(current_weather['sys']['sunrise'] + current_weather['timezone'])[4]:02}",
                205, 19)
            self.ssd.show_bitmap(self._load_icon("sun_rise"), 194, 19)
            self.ssd.show_string(f"{current_weather['main']['humidity']}%", 206, 34)
            self.ssd.show_bitmap(self._load_icon("humidity"), 194, 33)
            self.ssd.show_string(
                f"{localtime(current_weather['sys']['sunset'] + current_weather['timezone'])[3]:02}:{localtime(current_weather['sys']['sunset'] + current_weather['timezone'])[4]:02}",
                205, 50)
            self.ssd.show_bitmap(self._load_icon("sun_set"), 194, 49)
        else:
            self.ssd.show_string(f"{round(current_weather['main']['pressure'])} hPa", 205, 19)
            self.ssd.show_bitmap(self._load_icon("pressure"), 194, 18)
            self.ssd.show_string(
                f"{round(current_weather['wind']['speed'] * 3.6, 1)} km/s, {self.directions[round(current_weather['wind']['deg'] / 45) % 8]}",
                205, 34)
            self.ssd.show_bitmap(self._load_icon("wind"), 194, 33)
            self.ssd.show_string(f"{moon_state}", 205, 50)
            self.ssd.show_bitmap(self._load_icon("moon"), 194, 49)

    def display_forecast(self, cnt, forecast, offset_x=36):
        for idx in range(cnt):
            self.ssd.show_string(f"{localtime(forecast['list'][idx]['dt'])[3]:02}", 16 + (idx * offset_x), 74)
            self.ssd.show_bitmap(self._load_icon(forecast['list'][idx]['weather'][0]['icon']), 11 + (idx * offset_x),
                                 86)
            self.ssd.show_string(f"{round(forecast['list'][idx]['main']['temp'])}°", (
                15 + (idx * offset_x) if len(str(round(forecast['list'][idx]['main']['temp']))) == 2 else (
                    10 + (idx * offset_x) if len(str(round(forecast['list'][idx]['main']['temp']))) == 3 else 18 + (
                            idx * offset_x))), 116)


if __name__ == '__main__':
    ws = WeatherStation()

    ws.ssd.clear(ws.settings.theme())

    try:
        ws.prov.run(callback=lambda: (ws.display_bluetooth(), ws.ssd.update()))

        ws.ota_updater.download_and_install_update_if_available()

        data = ws.get_data(ws.settings.LAT, ws.settings.LON, ws.settings.CNT, ws.settings.UNITS, ws.settings.LANG,
                           ws.settings.API_KEY)

        if ws.battery.read_voltage() < 3.27:
            ws.display_low_battery()

        else:
            if data:
                ws.display_header(ws.battery.battery_percentage(), (data[1]['name']),
                                  localtime(data[1]['dt'] + data[1]['timezone']),
                                  json.load(open("version.json"))["version"])
                ws.display_info(data[1])
                ws.display_forecast(ws.settings.CNT, data[0])

        ws.ssd.update()

    except Exception as e:
        print(e)

    finally:
        ws.go_to_sleep()
