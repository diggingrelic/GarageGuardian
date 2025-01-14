from .Temperature import TemperatureDevice

class EnvironmentalSensorDevice(TemperatureDevice):
    """Base class for environmental sensors that measure multiple factors"""
    
    def get_pressure(self):
        """Get pressure in hPa"""
        raise NotImplementedError
        
    def get_altitude(self):
        """Get altitude in feet"""
        raise NotImplementedError