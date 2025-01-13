from ...interfaces.Temperature import TemperatureDevice

class MockTemperature(TemperatureDevice):
    """Mock implementation of a temperature sensor for testing
    
    Simulates a temperature/humidity sensor with configurable readings.
    """
    
    def __init__(self, initial_temp=20.0, initial_humidity=50.0):
        super().__init__()
        self._temperature = initial_temp
        self._humidity = initial_humidity
        self._last_reading = 0.0  # Direct assignment instead of await
        
    async def read(self):
        """Read current mock temperature and humidity"""
        await self.record_reading()
        return (self._temperature, self._humidity)
        
    async def is_working(self):
        """Check if mock sensor is functioning"""
        return await super().is_working()
        
    # Test helper methods
    async def set_setpoint(self, temp):
        """Set the mock temperature reading"""
        self._temperature = temp
        await self.record_reading()
        
    async def set_humidity(self, humidity):
        """Set the mock humidity reading"""
        self._humidity = humidity
        await self.record_reading()
        
    async def simulate_error(self):
        """Simulate a sensor error"""
        await self.record_error() 