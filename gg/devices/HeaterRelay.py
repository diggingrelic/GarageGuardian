from ..interfaces.Relay import RelayDevice
from ..config import PinConfig, SystemConfig
from machine import Pin # type: ignore
import time

class HeaterRelay(RelayDevice):
    """Heater control using relay on specified pin"""
    
    def __init__(self):
        super().__init__()
        pin_num = PinConfig.RELAY_PINS['HEATER']
        if pin_num is None:
            raise ValueError("Heater relay pin not configured")
            
        self._pin = Pin(pin_num, Pin.OUT)
        self._pin.off()  # Initialize to off state
        self._last_change = 0
        
    async def activate(self):
        """Turn heater on"""
        current_time = time.time()
        if not self.is_active():
            # Check cycle delay
            if current_time - self._last_change < SystemConfig.TEMP_SETTINGS['CYCLE_DELAY']:
                raise ValueError("Cannot activate: cycle delay not met")
                
        self._pin.on()
        self._last_change = current_time
        await self.record_reading()
        
    async def deactivate(self):
        """Turn heater off"""
        self._pin.off()
        self._last_change = time.time()
        await self.record_reading()
        
    async def is_active(self):
        """Check if heater is on"""
        await self.record_reading()
        return self._pin.value() == 1 