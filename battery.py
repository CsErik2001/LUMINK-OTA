from machine import ADC, Pin

class Battery:
    def __init__(self, pin_number, attenuation=ADC.ATTN_11DB, voltage_divider_factor=1.77):
        self.pin = ADC(Pin(pin_number))
        self.pin.init(atten=attenuation)  # Set attenuation to read up to 3.3V
        self.voltage_divider_factor = voltage_divider_factor

    def read_voltage(self):
        raw_value = self.pin.read_u16()  # Read the raw ADC value
        # Convert raw ADC value to voltage (assuming 16-bit resolution and 3.3V reference)
        voltage = (raw_value / 65535.0) * 3.3 * self.voltage_divider_factor
        return voltage

    def battery_percentage(self):
        voltage = self.read_voltage()

        # LiPo discharge curve lookup table (Voltage, Percentage)
        table = [
            (4.20, 100),
            (4.15, 95),
            (4.11, 90),
            (4.08, 85),
            (4.02, 80),
            (3.98, 75),
            (3.95, 70),
            (3.91, 65),
            (3.87, 60),
            (3.85, 55),
            (3.84, 50),
            (3.82, 45),
            (3.80, 40),
            (3.79, 35),
            (3.77, 30),
            (3.75, 25),
            (3.73, 20),
            (3.71, 15),
            (3.69, 10),
            (3.61, 5),
            (3.27, 0)
        ]

        if voltage >= table[0][0]:
            return 100
        if voltage <= table[-1][0]:
            return 0

        for i in range(len(table) - 1):
            v_high, p_high = table[i]
            v_low, p_low = table[i+1]

            if voltage >= v_low:
                # Linear interpolation
                return int(p_low + (voltage - v_low) * (p_high - p_low) / (v_high - v_low))

        return 0
