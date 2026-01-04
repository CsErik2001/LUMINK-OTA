import bluetooth
import json
from time import sleep
from machine import reset
from micropython import const
from c3pico import connect_wifi

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_CHAR_SSID_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_CHAR_PASS_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
_FLAG_WRITE = const(0x0008)


class BLEProvisioner:
    def __init__(self, ble_name="ESP32-Setup", config_file="wifi.json"):
        self.ble_name = ble_name
        self.config_file = config_file

        self._ble = bluetooth.BLE()
        self._connections = set()
        self.ssid = ""
        self.password = ""
        self.data_ready = False

        self._handle_ssid = None
        self._handle_pass = None

    def _load_config(self):
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
                return data["ssid"], data["pass"]
        except:
            return None, None

    def _save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump({"ssid": self.ssid, "pass": self.password}, f)
            print("MENTÉS: Adatok elmentve a flash memóriába.")
            return True
        except Exception as e:
            print(f"HIBA a mentésnél: {e}")
            return False

    def _setup_ble(self):
        self._ble.active(True)
        self._ble.config(mtu=500)
        self._ble.irq(self._irq)

        ((self._handle_ssid, self._handle_pass),) = self._ble.gatts_register_services([
            (_SERVICE_UUID, (
                (_CHAR_SSID_UUID, _FLAG_WRITE),
                (_CHAR_PASS_UUID, _FLAG_WRITE),
            )),
        ])

        self._advertise()
        print(f"BLE MÓD: Keresd a '{self.ble_name}' eszközt a telefonoddal!")

    def _advertise(self):
        name_bytes = bytes(self.ble_name, 'UTF-8')
        adv_data = bytearray(b'\x02\x01\x06') + bytearray((len(name_bytes) + 1, 0x09)) + name_bytes
        self._ble.gap_advertise(100000, adv_data)

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print("BLE: Telefon csatlakozva.")

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self._advertise()
            print("BLE: Telefon lecsatlakozva.")

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_ssid:
                self.ssid = self._ble.gatts_read(self._handle_ssid).decode('utf-8').strip()
                print(f"BLE: SSID érkezett: {self.ssid}")

            elif value_handle == self._handle_pass:
                self.password = self._ble.gatts_read(self._handle_pass).decode('utf-8').strip()
                print("BLE: Jelszó érkezett.")

                if self.ssid and self.password:
                    self.data_ready = True

    def _stop_ble(self):
        print("BLE: Leállítás...")
        self._ble.irq(None)
        sleep(0.2)
        self._ble.active(False)
        sleep(0.5)

    def run(self):

        ssid_saved, pass_saved = self._load_config()

        if ssid_saved and pass_saved:
            print(f"Mentett adatok betöltve ({ssid_saved}). Csatlakozás...")
            if connect_wifi(ssid_saved, pass_saved):
                print("\n==================================")
                print(" RENDSZER MŰKÖDIK (Wifi OK)")
                print("==================================")
                return True
            else:
                print("Sikertelen csatlakozás a mentett adatokkal.")

        print("Wifi kapcsolat nem jött létre. BLE Config indítása...")
        self._setup_ble()

        while not self.data_ready:
            sleep(0.5)

        print("\n--- Új adatok fogadva! ---")
        self._save_config()

        self._stop_ble()

        print("Újraindítás az új beállításokkal...")
        sleep(1)
        reset()