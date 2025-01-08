from .Base import BaseController
from gg.logging.Log import debug, error
from config import SystemConfig
import time

class TemperatureController(BaseController):
    """Manages temperature sensors and monitoring"""
    
    def __init__(self, name, temp_sensor, safety, events):
        super().__init__(name, temp_sensor, safety, events)
        self._last_temp = None
        self._check_interval = SystemConfig.UPDATE_INTERVALS['TEMPERATURE']
        self._last_check = 0
        
    async def initialize(self):
        """Initialize temperature monitoring"""
        debug("Initializing temperature controller")
        if not await super().initialize():
            error("Temperature sensor initialization failed")
            return False
            
        # Use the reading we already have
        self._last_temp = self.hardware.get_fahrenheit()
        self._last_check = time.time()
        
        # Publish initial temperature
        await self.publish_event("temperature_current", {
            "temp": self._last_temp,
            "timestamp": self._last_check
        })
        debug(f"Temperature controller initialized, enabled={self.enabled}")
        return True
            
    async def monitor(self):
        """Monitor temperature and publish changes"""
        if not self.enabled:
            return
            
        current_time = time.time()
        if current_time - self._last_check < self._check_interval:
            return
            
        try:
            current_temp = self.hardware.get_fahrenheit()  # This will raise if reading fails
            self._last_check = current_time
            debug(f"Publishing temperature_current event: {current_temp}°F")
                
            # Always publish current reading
            await self.publish_event("temperature_current", {
                "temp": current_temp,
                "timestamp": current_time
            })
                
            # Publish changes if significant
            if (self._last_temp is None or 
                abs(current_temp - self._last_temp) >= SystemConfig.TEMP_SETTINGS['TEMP_DIFFERENTIAL']):
                await self.publish_event("temperature_changed", {
                    "temp": current_temp,
                    "previous": self._last_temp,
                    "timestamp": current_time
                })
                self._last_temp = current_temp
                
        except Exception as e:
            error(f"Temperature monitoring failed: {e}")
            raise  # Re-raise to ensure errors are caught
            
    async def cleanup(self):
        """Clean up temperature monitoring"""
        await super().cleanup()
        self._last_temp = None
        self._last_check = 0 