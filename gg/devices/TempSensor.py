from ..interfaces.Temperature import TemperatureDevice
from ..logging.Log import error, debug
from machine import I2C, Pin # type: ignore
from config import I2CConfig
import time

class TempSensorADT7410(TemperatureDevice):
    """ADT7410 temperature sensor implementation"""
    
    def __init__(self, i2c):
        super().__init__()
        self.i2c = i2c
        self.address = 0x48  # Default I2C address for ADT7410
        self._last_read = 0
        self._read_interval = 0.1  # 100ms minimum between reads
        
    def get_fahrenheit(self):
        """Get temperature in Fahrenheit directly from sensor"""
        current_time = time.time()
        if current_time - self._last_read < self._read_interval:
            return None
            
        try:
            self._last_read = current_time
            data = self.i2c.readfrom(self.address, 2)
            temp = (data[0] << 8 | data[1]) >> 3
            if temp & 0x1000:
                temp = temp - 8192
            # Convert directly to Fahrenheit
            return (temp * 0.0625 * 9/5) + 32
        except Exception as e:
            error(f"Temperature read failed: {e}")
            return None
            
    async def is_working(self):
        """Check if sensor is responding"""
        try:
            devices = self.i2c.scan()
            return self.address in devices
        except Exception:
            return False 

    async def initialize(self):
        """Initialize the temperature sensor"""
        try:
            if await self.is_working():
                # Get initial reading to verify sensor
                temp = self.get_fahrenheit()
                if temp is not None:
                    debug(f"Temperature sensor initialized: {temp}°F")
                    return True
            error("Temperature sensor not responding")
            return False
        except Exception as e:
            error(f"Temperature sensor initialization failed: {e}")
            return False 