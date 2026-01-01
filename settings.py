class Settings:
    def __init__(self):
        self.SSID = "UPCDA5F825"                                                            # WIFI SSID
        self.PASSWORD = "kK8fkkvuyeSm."                                                     # WIFI PASSWORD

        self.FIRMWARE_URL = "https://raw.githubusercontent.com/CsErik2001/LUMINK-OTA/"      # GITHUB URL FOR THE FIRMWARE
        self.BRANCH = "weather_station"                                                     # GITHUB BRANCH NAME

        self.API_KEY = "47c3f9b791abd63c01da2c6a50f596b6"                                   # API KEY
        self.LAT = 47.685                                                                   # EXAMPLE - Budapest, HU
        self.LON = 16.59                                                                    # EXAMPLE - Budapest, HU
        self.CNT = 8                                                                        # default is 8.
        self.UNITS = "metric"                                                               # metric / imperial
        self.LANG = "en"                                                                    # tested with 'en'

        self.THEME = "light"                                                                # dark or light

        self.DELAY = 900                                                                    # in seconds default 900 seconds = 15 mins.
        self.OFFSET = 15                                                                    # WIFI timeout offset, default = 15

    def theme(self):
        if self.THEME == "dark":
            return 0x00
        else:
            return 0xff
