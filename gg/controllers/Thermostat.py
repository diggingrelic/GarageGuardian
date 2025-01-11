from .Base import BaseController
from ..logging.Log import debug, error, info
from config import SystemConfig
import time
import asyncio

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
        self.heater_enabled = False
        self._pending_disable = False
        
        debug("=== Initializing Thermostat ===")
        debug("Subscribing to temperature events")
        debug(f"Events system has {self.events.subscribers}")
        self.events.subscribe("temperature_current", self.handle_temperature)
        debug(f"After subscribe: {self.events.subscribers}")
        
    async def initialize(self):
        """Initialize the thermostat hardware"""
        await super().initialize()
        await self.hardware.deactivate()
        debug("Thermostat hardware initialized")
        return True
        
    async def handle_temperature(self, data):
        """Handle temperature update events"""
        try:
            if "temp" not in data:
                error("Missing temperature data in event")
                raise ValueError("Invalid temperature event format")
                
            if data["temp"] is None:
                error("Temperature reading is None")
                raise ValueError("Invalid temperature reading")
                
            self._current_temp = float(data["temp"])
            await self._check_thermostat()
            
        except Exception as e:
            error(f"Error in temperature handler: {e}")
            if await self.hardware.is_active():
                await self._turn_off()
            raise
            
    async def enable_heater(self):
        """Enable heater control"""
        debug("=== Enabling Heater ===")
        
        # Just use our current temperature - we know it's being updated via events
        if self._current_temp is None:
            error("No temperature reading available")
            return False
            
        self.heater_enabled = True
        self._pending_disable = False
        
        debug(f"heater_enabled set to: {self.heater_enabled}")
        debug(f"current_temp is: {self._current_temp}°F")
        debug(f"setpoint is: {self.setpoint}°F")
        
        await self.publish_event("heater_enabled", {
            "timestamp": time.time(),
            "temp": self._current_temp,
            "setpoint": self.setpoint
        })
        
        debug("Checking thermostat after enable")
        await self._check_thermostat()
        return True
        
    async def disable_heater(self):
        """Disable heater control"""
        self._pending_disable = True
        await self._check_thermostat()
        
    async def _check_thermostat(self):
        """Check if heater should be on/off based on current temperature"""
        try:
            if not self.heater_enabled or self._current_temp is None:
                if await self.hardware.is_active():
                    debug("Heater disabled or no temperature, turning off")
                    await self._turn_off()
                return
                
            current_time = time.time()
            setpoint = float(self.setpoint)
            
            # If heater is on, check if it should turn off
            if await self.hardware.is_active():
                if current_time - self._last_on_time < self._min_run_time:
                    return
                    
                if self._current_temp >= setpoint + self._differential:
                    debug(f"*** Temperature {self._current_temp}°F above setpoint {setpoint}°F + differential, turning OFF ***")
                    await self._turn_off()
                    
            # If heater is off, check if it should turn on
            else:
                time_since_off = current_time - self._last_off_time
                if time_since_off < self._cycle_delay:
                    remaining = int(self._cycle_delay - time_since_off)
                    if not hasattr(self, '_cycle_delay_notified'):
                        debug(f"Status: Temp={self._current_temp}°F, Setpoint={setpoint}°F - Cycle delay in effect")
                        self._cycle_delay_notified = True
                    elif remaining % 5 == 0:  # Only log every 5 seconds
                        debug(f"Cycle delay: {remaining}s remaining")
                    return
                    
                # Reset notification flag when cycle delay is met
                self._cycle_delay_notified = False
                
                if self._current_temp <= setpoint - self._differential:
                    debug(f"*** Temperature {self._current_temp}°F below setpoint {setpoint}°F - differential, attempting to turn ON ***")
                    await self._turn_on()
                    
        except Exception as e:
            error(f"Thermostat check failed: {e}")
            # Disable heater on errors for safety
            if await self.hardware.is_active():
                await self._turn_off()
            raise
            
    async def _turn_on(self):
        """Turn heater on"""
        await self.hardware.activate()
        self._last_on_time = time.time()
        await self.publish_event("heater_activated", {
            "temp": self._current_temp,
            "setpoint": self.setpoint,
            "timestamp": self._last_on_time
        })
        
    async def _turn_off(self):
        """Turn heater off"""
        await self.hardware.deactivate()
        self._last_off_time = time.time()
        await self.publish_event("heater_deactivated", {
            "temp": self._current_temp,
            "setpoint": self.setpoint,
            "timestamp": self._last_off_time
        }) 
        
    async def monitor(self):
        """Monitor thermostat state"""
        if not self.enabled:
            return
            
        try:
            await self._check_thermostat()
        except Exception as e:
            error(f"Thermostat monitoring failed: {e}")
            
    async def cleanup(self):
        """Clean up thermostat"""
        await super().cleanup()
        # Ensure heater is off
        try:
            await self.hardware.deactivate()
        except Exception as e:
            await self.publish_error(f"Cleanup failed: {e}") 
        
    async def set_temperature(self, setpoint):
        """Set the target temperature"""
        try:
            if setpoint < SystemConfig.TEMP_SETTINGS['MIN_TEMP'] or \
               setpoint > SystemConfig.TEMP_SETTINGS['MAX_TEMP']:
                return False
                
            self.setpoint = setpoint
            await self.publish_event("thermostat_setpoint", {
                "setpoint": setpoint,
                "timestamp": time.time()
            })
            debug(f"Setpoint changed to {setpoint}°F")
            return True
            
        except Exception as e:
            error(f"Failed to set temperature: {e}")
            return False 
        
    async def set_cycle_delay(self, delay):
        """Set the cycle delay"""
        try:
            if delay < 0:
                return False
                
            SystemConfig.TEMP_SETTINGS['CYCLE_DELAY'] = delay
            self._cycle_delay = delay
            await self.publish_event("thermostat_cycle_delay", {
                "delay": delay,
                "timestamp": time.time()
            })
            debug(f"Cycle delay changed to {delay}s")
            return True
            
        except Exception as e:
            error(f"Failed to set cycle delay: {e}")
            return False 