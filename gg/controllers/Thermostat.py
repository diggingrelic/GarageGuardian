from .Base import BaseController
from ..config import SystemConfig
import time

class ThermostatController(BaseController):
    """Controls heater based on temperature events"""
    
    def __init__(self, name, heater_relay, safety, events):
        super().__init__(name, heater_relay, safety, events)
        self.setpoint = SystemConfig.TEMP_SETTINGS['DEFAULT_SETPOINT']
        self._min_run_time = SystemConfig.TEMP_SETTINGS['MIN_RUN_TIME']
        self._cycle_delay = SystemConfig.TEMP_SETTINGS['CYCLE_DELAY']
        self._differential = SystemConfig.TEMP_SETTINGS['TEMP_DIFFERENTIAL']
        self._last_off_time = 0
        self._last_on_time = 0
        self._current_temp = None
        
    async def initialize(self):
        """Initialize the thermostat"""
        await super().initialize()
        # Subscribe to temperature events
        self.events.subscribe("temperature_current", self.handle_temperature)
        # Ensure heater starts in known state
        await self.hardware.deactivate()
        return True
        
    async def handle_temperature(self, data):
        """Handle temperature update events"""
        self._current_temp = data["temp"]
        await self._check_thermostat()
        
    async def set_temperature(self, temp):
        """Set target temperature"""
        if SystemConfig.TEMP_SETTINGS['MIN_TEMP'] <= temp <= SystemConfig.TEMP_SETTINGS['MAX_TEMP']:
            self.setpoint = temp
            await self.publish_event("setpoint_changed", {
                "temp": temp,
                "timestamp": time.time()
            })
            await self._check_thermostat()
            return True
        return False
        
    async def _check_thermostat(self):
        """Check if heater state should change"""
        if self._current_temp is None:
            return
            
        try:
            if await self.hardware.is_active():
                # Check if we've met minimum run time and should turn off
                if time.time() - self._last_on_time >= self._min_run_time:
                    if self._current_temp >= self.setpoint + self._differential:
                        await self._turn_off()
            else:
                # Check if we can turn on (cycle delay)
                if time.time() - self._last_off_time >= self._cycle_delay:
                    if self._current_temp <= self.setpoint - self._differential:
                        await self._turn_on()
                        
        except Exception as e:
            await self.publish_error(f"Thermostat check failed: {e}")
            
    async def _turn_on(self):
        """Turn heater on with event notification"""
        await self.hardware.activate()
        self._last_on_time = time.time()
        await self.publish_event("heater_on", {
            "temp": self._current_temp,
            "setpoint": self.setpoint,
            "timestamp": time.time()
        })
        
    async def _turn_off(self):
        """Turn heater off with event notification"""
        await self.hardware.deactivate()
        self._last_off_time = time.time()
        await self.publish_event("heater_off", {
            "temp": self._current_temp,
            "setpoint": self.setpoint,
            "timestamp": time.time()
        }) 
        
    async def monitor(self):
        """Monitor thermostat state"""
        if not self.enabled:
            return
            
        try:
            # Check thermostat state based on current temperature
            await self._check_thermostat()
        except Exception as e:
            await self.publish_error(f"Thermostat monitoring failed: {e}")
            
    async def cleanup(self):
        """Clean up thermostat"""
        await super().cleanup()
        # Ensure heater is off
        try:
            await self.hardware.deactivate()
        except Exception as e:
            await self.publish_error(f"Cleanup failed: {e}") 