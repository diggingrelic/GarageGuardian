from .Base import BaseDevice

class TemperatureDevice(BaseDevice):
    """Interface for temperature sensor hardware"""
    
    def read(self):
        """Read current temperature and humidity
        
        Returns:
            tuple: (temperature in C, humidity percentage)
        """
        raise NotImplementedError 