"""
MicroPython driver for BMP390 sensor based on Adafruit's CircuitPython implementation
"""
from machine import I2C, Pin
import time
import struct

class BMP390:
    # Register addresses
    _CHIP_ID = 0x00
    _REGISTER_STATUS = 0x03
    _REGISTER_PRESSUREDATA = 0x04
    _REGISTER_TEMPDATA = 0x07
    _REGISTER_CONTROL = 0x1B
    _REGISTER_OSR = 0x1C
    _REGISTER_ODR = 0x1D
    _REGISTER_CONFIG = 0x1F
    _REGISTER_CAL_DATA = 0x31
    _REGISTER_CMD = 0x7E

    # OSR (Over-sampling) and Filter settings
    OSR_SETTINGS = (1, 2, 4, 8, 16, 32)  # pressure and temperature
    IIR_SETTINGS = (0, 2, 4, 8, 16, 32, 64, 128)  # IIR filter coefficients
    
    def __init__(self, i2c, address=0x77):
        self.i2c = i2c
        self.address = address
        
        # Read and verify chip ID
        chip_id = self._read_byte(self._CHIP_ID)
        if chip_id != 0x60:  # BMP390
            raise RuntimeError(f"Failed to find BMP390! Chip ID 0x{chip_id:02x}")
        
        # Read calibration data
        self._read_coefficients()
        
        # Reset device
        self.reset()
        
        # Set default configuration
        self.sea_level_pressure = 101325  # Pressure at sea level in Pa
        self._wait_time = 0.002  # Delay between readings
        
        # Default settings
        self.pressure_oversampling = 8    # x8 oversampling
        self.temperature_oversampling = 2  # x2 oversampling
        self.filter_coefficient = 4        # IIR filter coefficient
        
    def reset(self):
        """Perform a power-on-reset."""
        self._write_register_byte(self._REGISTER_CMD, 0xB6)
        time.sleep_ms(10)
        
    def _read_coefficients(self):
        """Read factory calibration coefficients."""
        coeff = self._read_register(self._REGISTER_CAL_DATA, 21)
        coeff = struct.unpack('<HHbhhbbHHbbhbb', coeff)  # Unpack calibration data
        
        # Convert coefficient to proper scaling per datasheet
        self._temp_calib = (
            coeff[0] / 2**-8.0,  # T1
            coeff[1] / 2**30.0,  # T2
            coeff[2] / 2**48.0   # T3
        )
        
        self._pressure_calib = (
            (coeff[3] - 2**14.0) / 2**20.0,  # P1
            (coeff[4] - 2**14.0) / 2**29.0,  # P2
            coeff[5] / 2**32.0,              # P3
            coeff[6] / 2**37.0,              # P4
            coeff[7] / 2**-3.0,              # P5
            coeff[8] / 2**6.0,               # P6
            coeff[9] / 2**8.0,               # P7
            coeff[10] / 2**15.0,             # P8
            coeff[11] / 2**48.0,             # P9
            coeff[12] / 2**48.0,             # P10
            coeff[13] / 2**65.0              # P11
        )
        
    def read(self):
        """Read temperature and pressure."""
        # Trigger a measurement
        self._write_register_byte(self._REGISTER_CONTROL, 0x13)  # Enable pressure and temp
        
        # Wait for measurement to complete
        while self._read_byte(self._REGISTER_STATUS) & 0x60 != 0x60:
            time.sleep(self._wait_time)
        
        # Read raw values
        data = self._read_register(self._REGISTER_PRESSUREDATA, 6)
        adc_p = data[2] << 16 | data[1] << 8 | data[0]
        adc_t = data[5] << 16 | data[4] << 8 | data[3]
        
        # Temperature compensation
        T1, T2, T3 = self._temp_calib
        pd1 = adc_t - T1
        pd2 = pd1 * T2
        temperature = pd2 + (pd1 * pd1) * T3
        
        # Pressure compensation
        P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11 = self._pressure_calib
        
        pd1 = P6 * temperature
        pd2 = P7 * pow(temperature, 2)
        pd3 = P8 * pow(temperature, 3)
        po1 = P5 + pd1 + pd2 + pd3
        
        pd1 = P2 * temperature
        pd2 = P3 * pow(temperature, 2)
        pd3 = P4 * pow(temperature, 3)
        po2 = adc_p * (P1 + pd1 + pd2 + pd3)
        
        pd1 = pow(adc_p, 2)
        pd2 = P9 + P10 * temperature
        pd3 = pd1 * pd2
        pd4 = pd3 + P11 * pow(adc_p, 3)
        
        pressure = po1 + po2 + pd4
        
        return temperature, pressure
    
    def read_temperature(self):
        """Read temperature in degrees Celsius."""
        temp, _ = self.read()
        return temp
    
    def read_pressure(self):
        """Read pressure in Pascals."""
        _, press = self.read()
        return press
    
    def read_altitude(self, sea_level_pa=101325.0):
        """Calculate altitude in meters."""
        pressure = self.read_pressure()
        return 44307.7 * (1 - (pressure / sea_level_pa) ** 0.190284)
    
    def _read_byte(self, register):
        """Read single byte from register."""
        return self.i2c.readfrom_mem(self.address, register, 1)[0]
    
    def _read_register(self, register, length):
        """Read multiple bytes from registers."""
        return self.i2c.readfrom_mem(self.address, register, length)
    
    def _write_register_byte(self, register, value):
        """Write single byte to register."""
        self.i2c.writeto_mem(self.address, register, bytes([value]))