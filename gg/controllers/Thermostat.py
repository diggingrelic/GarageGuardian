from .Base import BaseController
from .thermostat_states import (
    ThermostatStateManager, 
    STATE_IDLE, 
    STATE_HEATING, 
    STATE_CYCLE_DELAY, 
    STATE_MIN_RUN, 
    STATE_DISABLED
)
from ..logging.Log import debug, error, info
from config import SystemConfig
import time
import asyncio

class ThermostatController(BaseController):
    """Controls heater based on temperature events"""
    
    def __init__(self, name, heater_relay, safety, events):
        super().__init__(name, heater_relay, safety, events)
        config = SystemConfig.get_instance()
        self.setpoint = config.TEMP_SETTINGS['DEFAULT_SETPOINT']
        self._min_run_time = config.TEMP_SETTINGS['MIN_RUN_TIME']
        self._cycle_delay = config.TEMP_SETTINGS['CYCLE_DELAY']
        self._differential = config.TEMP_SETTINGS['TEMP_DIFFERENTIAL']
        self._last_off_time = time.time()  # Initialize to current time
        self._last_on_time = 0
        self._current_temp = None
        self.heater_enabled = False
        self._state_manager = ThermostatStateManager(self)
        
        self.events.subscribe("temperature_current", self.handle_temperature)
        
    async def initialize(self):
        """Initialize the thermostat hardware"""
        await super().initialize()
        await self.hardware.deactivate()
        await self._state_manager.transition(STATE_IDLE)
        return True
        
    async def handle_temperature(self, data):
        """Handle temperature update events"""
        try:
            if "temp" not in data or data["temp"] is None:
                error("Invalid temperature data")
                return
                
            self._current_temp = float(data["temp"])
            await self._check_thermostat()
            
        except Exception as e:
            error(f"Error in temperature handler: {e}")
            if await self.hardware.is_active():
                await self._turn_off()
            raise
            
    async def enable_heater(self):
        """Enable heater control"""
        if self._current_temp is None:
            error("No temperature reading available")
            return False
            
        self.heater_enabled = True
        await self._state_manager.transition(STATE_IDLE)
        
        await self.publish_event("heater_enabled", {
            "timestamp": time.time(),
            "temp": self._current_temp,
            "setpoint": self.setpoint
        })
        
        await self._check_thermostat()
        return True
        
    async def disable_heater(self):
        """Disable heater control"""
        self.heater_enabled = False
        await self._state_manager.transition(STATE_DISABLED)
        await self._check_thermostat()
        
    async def _check_thermostat(self):
        """Check if heater should be on/off based on current temperature"""
        try:
            current_time = time.time()
            
            # Check minimum run time before any other checks
            if await self.hardware.is_active():
                time_since_on = current_time - self._last_on_time
                if time_since_on < self._min_run_time:
                    await self._state_manager.transition(STATE_MIN_RUN)
                    return
            
            if not self.heater_enabled or self._current_temp is None:
                if await self.hardware.is_active():
                    if current_time - self._last_on_time >= self._min_run_time:
                        await self._turn_off()
                await self._state_manager.transition(STATE_DISABLED)
                return
                
            setpoint = float(self.setpoint)
            
            # If heater is on, check if it should turn off
            if await self.hardware.is_active():
                if self._current_temp >= setpoint + self._differential:
                    if current_time - self._last_on_time >= self._min_run_time:
                        await self._turn_off()
                        await self._state_manager.transition(STATE_IDLE)
                    
            # If heater is off, check if it should turn on
            else:
                time_since_off = current_time - self._last_off_time
                
                if time_since_off < self._cycle_delay:
                    await self._state_manager.transition(STATE_CYCLE_DELAY)
                    return
                    
                # Only attempt to turn on if cycle delay has elapsed
                if time_since_off >= self._cycle_delay and \
                   self._current_temp <= setpoint - self._differential:
                    await self._turn_on()
                    await self._state_manager.transition(STATE_HEATING)
                else:
                    await self._state_manager.transition(STATE_IDLE)
                    
        except Exception as e:
            error(f"Thermostat check failed: {e}")
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
        await self._check_thermostat()
            
    async def cleanup(self):
        """Clean up thermostat"""
        await super().cleanup()
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
            
    async def reset_cycle_delay(self):
        """Reset cycle delay timing"""
        self._last_off_time = time.time()
        debug("Cycle delay timer reset") 
        
    async def handle_config_update(self, setting, value):
        """Handle configuration updates"""
        if setting == 'MIN_RUN_TIME':
            self._min_run_time = value
            debug(f"Updated minimum run time to {value}s")
        elif setting == 'CYCLE_DELAY':
            self._cycle_delay = value
            debug(f"Updated cycle delay to {value}s")
        elif setting == 'TEMP_DIFFERENTIAL':
            self._differential = value
            debug(f"Updated temperature differential to {value}°F") 