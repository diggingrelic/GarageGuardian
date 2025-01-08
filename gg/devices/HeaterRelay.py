from ..interfaces.Relay import RelayDevice
from ..logging.Log import error, debug
from machine import Pin
from config import PinConfig, SystemConfig
import time

class HeaterRelay(RelayDevice):
    """Heater control using relay with status LED"""
    
    def __init__(self):
        super().__init__()
        # Initialize relay pin
        pin_num = PinConfig.RELAY_PINS['HEATER']
        if pin_num is None:
            raise ValueError("Heater relay pin not configured")
        self._pin = Pin(pin_num, Pin.OUT)
        
        # Initialize status LED
        led_pin = PinConfig.STATUS_LEDS['HEATER']
        if isinstance(led_pin, str) and led_pin == "LED":
            self._led = Pin("LED", Pin.OUT)  # Onboard LED
        elif isinstance(led_pin, (int, str)):
            self._led = Pin(led_pin, Pin.OUT)
        else:
            self._led = None
            
        # Initialize state
        self._last_change = 0
        self.deactivate()  # Start in known state
        
    async def activate(self):
        """Turn heater on"""
        current_time = time.time()
        if not await self.is_active():
            # Check cycle delay
            if current_time - self._last_change < SystemConfig.TEMP_SETTINGS['CYCLE_DELAY']:
                raise ValueError("Cannot activate: cycle delay not met")
                
        debug("Activating heater relay")
        self._pin.on()
        if self._led:
            self._led.on()
        self._last_change = current_time
        
    async def deactivate(self):
        """Turn heater off"""
        debug("Deactivating heater relay")
        self._pin.off()
        if self._led:
            self._led.off()
        self._last_change = time.time()
        
    async def is_active(self):
        """Check if relay is active"""
        return bool(self._pin.value()) 