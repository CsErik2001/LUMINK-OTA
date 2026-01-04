from machine import ADC, Pin

class Battery:
    # Battery Specs:
    # Model: 803450
    # Type: Lithium battery
    # Capacity: 2000mAh
    # Rated Voltage: 3.7v
    # Dimensions: 34x50x8mm

    def __init__(self, pin_number, min_voltage=3.0, max_voltage=4.2, attenuation=ADC.ATTN_11DB, voltage_divider_factor=2.0):
        self.pin = ADC(Pin(pin_number))
        self.pin.init(atten=attenuation)
        self.voltage_divider_factor = voltage_divider_factor
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage

    def read_voltage(self):
        raw_value = self.pin.read_u16()
        voltage = (raw_value / 65535.0) * 3.3 * self.voltage_divider_factor
        return voltage

    def battery_percentage(self):
        voltage = self.read_voltage()
        percentage = int(((voltage - self.min_voltage) / (self.max_voltage - self.min_voltage)) * 100)
        return max(0, min(100, percentage))
