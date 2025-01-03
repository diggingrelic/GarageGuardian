from ...hardware.interfaces.Temperature import TemperatureDevice
from typing import Tuple

class MockTemperature(TemperatureDevice):
    """Mock implementation of a temperature sensor for testing
    
    Simulates a temperature/humidity sensor with configurable readings.
    """
    
    def __init__(self, initial_temp: float = 20.0, initial_humidity: float = 50.0):
        super().__init__()
        self._temperature = initial_temp
        self._humidity = initial_humidity
        self.record_reading()
        
    def read(self) -> Tuple[float, float]:
        """Read current mock temperature and humidity"""
        self.record_reading()
        return (self._temperature, self._humidity)
        
    def is_working(self) -> bool:
        """Check if mock sensor is functioning"""
        return self._error_count < self._max_errors
        
    # Test helper methods
    def set_temperature(self, temp: float):
        """Set the mock temperature reading
        
        Args:
            temp (float): Temperature in Celsius
        """
        self._temperature = temp
        self.record_reading()
        
    def set_humidity(self, humidity: float):
        """Set the mock humidity reading
        
        Args:
            humidity (float): Humidity percentage
        """
        self._humidity = humidity
        self.record_reading()
        
    def simulate_error(self):
        """Simulate a sensor error"""
        self.record_error() 