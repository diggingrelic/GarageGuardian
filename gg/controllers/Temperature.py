from ..interfaces.Temperature import TemperatureDevice
from .Base import BaseController

class TemperatureController(BaseController):
    """Controller for temperature sensor operations
    
    Manages a temperature sensor and integrates it with the event system.
    Monitors temperature changes and publishes events when thresholds
    are crossed.
    
    Events published:
        - temperature_changed: When temperature changes significantly
        - humidity_changed: When humidity changes significantly
        - temperature_alert: When temperature exceeds thresholds
        - temperature_error: When sensor operation fails
    """
    
    def __init__(self, sensor: TemperatureDevice, event_system):
        super().__init__(sensor, event_system)
        self._last_temp = None
        self._last_humidity = None
        self._temp_threshold = 0.5  # Minimum change to report
        self._humidity_threshold = 1.0
        self._high_temp_alert = 30.0
        self._low_temp_alert = 10.0
        
    async def monitor(self):
        """Monitor temperature and humidity changes"""
        if not self.should_check():
            return
            
        try:
            temp, humidity = self.device.read()
            
            # Check for significant temperature change
            if (self._last_temp is None or 
                abs(temp - self._last_temp) >= self._temp_threshold):
                await self.publish_event("temperature_changed", {
                    "temperature": temp,
                    "previous": self._last_temp
                })
                self._last_temp = temp
                
            # Check for significant humidity change
            if (self._last_humidity is None or 
                abs(humidity - self._last_humidity) >= self._humidity_threshold):
                await self.publish_event("humidity_changed", {
                    "humidity": humidity,
                    "previous": self._last_humidity
                })
                self._last_humidity = humidity
                
            # Check temperature thresholds
            if temp >= self._high_temp_alert:
                await self.publish_event("temperature_alert", {
                    "temperature": temp,
                    "type": "high"
                })
            elif temp <= self._low_temp_alert:
                await self.publish_event("temperature_alert", {
                    "temperature": temp,
                    "type": "low"
                })
                
        except Exception as e:
            await self.publish_error(f"Reading failed: {e}")
            
    def set_thresholds(self, temp_change: float = None, 
                      humidity_change: float = None,
                      high_temp: float = None,
                      low_temp: float = None):
        """Update monitoring thresholds
        
        Args:
            temp_change (float, optional): Minimum temperature change to report
            humidity_change (float, optional): Minimum humidity change to report
            high_temp (float, optional): High temperature alert threshold
            low_temp (float, optional): Low temperature alert threshold
        """
        if temp_change is not None:
            self._temp_threshold = temp_change
        if humidity_change is not None:
            self._humidity_threshold = humidity_change
        if high_temp is not None:
            self._high_temp_alert = high_temp
        if low_temp is not None:
            self._low_temp_alert = low_temp 