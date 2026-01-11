from machine import ADC, Pin


class Battery:
    def __init__(self, pin_number, min_voltage=3.0, max_voltage=4.2, voltage_divider_factor=2.0):
        self.pin = ADC(Pin(pin_number))
        self.pin.atten(ADC.ATTN_11DB)
        self.voltage_divider_factor = voltage_divider_factor
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage

    def read_voltage(self):
        microvolts = self.pin.read_uv()
        volts_at_pin = microvolts / 1_000_000
        real_voltage = volts_at_pin * self.voltage_divider_factor
        return round(real_voltage, 2)

    def battery_percentage(self):
        voltage = self.read_voltage()
        pct = (voltage - self.min_voltage) / (self.max_voltage - self.min_voltage) * 100
        pct = max(0, min(100, pct))
        return int(pct)