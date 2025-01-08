from .Device import Device

class TemperatureDevice(Device):
    """Interface for temperature sensors"""
    
    def get_fahrenheit(self):
        """Get temperature in Fahrenheit"""
        raise NotImplementedError
        
    def get_celsius(self):
        """Get temperature in Celsius"""
        raise NotImplementedError 