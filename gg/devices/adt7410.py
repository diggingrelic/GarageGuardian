import time

class TempSensorADT7410:
    def __init__(self, i2c, address=0x48):
        """
        Initializes the ADT7410 sensor on the specified I2C bus and address.
        """
        self.i2c = i2c
        self.address = address
        self._check_sensor()
        self._reset_sensor()
        self._initialize_sensor()

    def _check_sensor(self):
        """
        Scans the I2C bus to ensure the sensor is connected.
        """
        #print("Scanning I2C bus...")
        devices = self.i2c.scan()
        #print(f"Found I2C devices: {devices}")
        if self.address not in devices:
            raise RuntimeError(f"Sensor not found at address {hex(self.address)}.")

    def _reset_sensor(self):
        """
        Sends a software reset command to the sensor.
        """
        reset_register = 0x2F
        for attempt in range(3):
            try:
                self.i2c.writeto_mem(self.address, reset_register, bytearray([0x00]))
                time.sleep(1)  # Allow time for the reset
                return
            except OSError:
                pass  # Suppress non-fatal errors
        raise RuntimeError("Failed to reset the sensor after 3 attempts.")

    def _initialize_sensor(self):
        """
        Configures the ADT7410 sensor for 16-bit resolution and continuous mode.
        """
        config_register = 0x03
        config_value = 0b01110000  # 16-bit mode, continuous conversion
        time.sleep(1)  # Allow sensor to stabilize before initialization
        for attempt in range(3):
            try:
                self.i2c.writeto_mem(self.address, config_register, bytearray([config_value]))
                time.sleep(0.5)  # Allow sensor to stabilize
                return
            except OSError:
                pass  # Suppress non-fatal errors
        raise RuntimeError("Failed to initialize the sensor after 3 attempts.")

    def get_fahrenheit(self):
        """
        Reads the raw temperature data and converts it to Fahrenheit.
        """
        temp_register = 0x00
        try:
            data = self.i2c.readfrom_mem(self.address, temp_register, 2)
            msb = data[0]
            lsb = data[1]
            raw_temp = (msb << 8) | lsb

            # Convert to signed 16-bit integer
            if raw_temp & 0x8000:
                raw_temp -= 1 << 16

            celsius = raw_temp / 128.0
            return (celsius * 1.8) + 32
        except OSError:
            return None
