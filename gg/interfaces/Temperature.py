from .Device import Device
from ..logging.Log import debug, error

class TemperatureDevice(Device):
    """Base class for temperature sensors"""
    
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
            
    async def is_working(self):
        """Check if sensor is responding"""
        return True
        
    def get_fahrenheit(self):
        """Get temperature in Fahrenheit - must be implemented by subclass"""
        raise NotImplementedError("get_fahrenheit must be implemented") 