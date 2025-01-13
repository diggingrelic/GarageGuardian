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
        self.config = SystemConfig.get_instance()
        
        # Non-persistent state
        self._last_off_time = time.time()
        self._last_on_time = 0
        self._current_temp = None
        self._state_manager = ThermostatStateManager(self)
        
        # Subscribe to events
        self.events.subscribe("temperature_current", self.handle_temperature)
        self.events.subscribe("thermostat_timer_start", self._handle_timer_start)
        self.events.subscribe("thermostat_timer_end", self._handle_timer_end)
        
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
            
        self.config.TEMP_SETTINGS['HEATER_MODE'] = 'heat'
        await self._state_manager.transition(STATE_IDLE)
        
        await self.publish_event("heater_enabled", {
            "timestamp": time.time(),
            "temp": self._current_temp,
            "setpoint": self.config.TEMP_SETTINGS['SETPOINT']
        })
        
        await self._check_thermostat()
        return True
        
    async def disable_heater(self):
        """Disable heater control"""
        self.config.TEMP_SETTINGS['HEATER_MODE'] = 'off'
        await self._state_manager.transition(STATE_DISABLED)
        await self._check_thermostat()
        
    async def _check_thermostat(self):
        """Check if heater should be on/off based on current temperature"""
        try:
            current_time = time.time()
            
            # Check minimum run time before any other checks
            if await self.hardware.is_active():
                time_since_on = current_time - self._last_on_time
                if time_since_on < self.config.TEMP_SETTINGS['MIN_RUN_TIME']:
                    await self._state_manager.transition(STATE_MIN_RUN)
                    return
            
            if not self.heater_enabled or self._current_temp is None:
                if await self.hardware.is_active():
                    if current_time - self._last_on_time >= self.config.TEMP_SETTINGS['MIN_RUN_TIME']:
                        await self._turn_off()
                await self._state_manager.transition(STATE_DISABLED)
                return
                
            setpoint = float(self.config.TEMP_SETTINGS['SETPOINT'])
            
            # If heater is on, check if it should turn off
            if await self.hardware.is_active():
                if self._current_temp >= setpoint + self.config.TEMP_SETTINGS['TEMP_DIFFERENTIAL']:
                    if current_time - self._last_on_time >= self.config.TEMP_SETTINGS['MIN_RUN_TIME']:
                        await self._turn_off()
                        await self._state_manager.transition(STATE_IDLE)
                    
            # If heater is off, check if it should turn on
            else:
                time_since_off = current_time - self._last_off_time
                
                if time_since_off < self.config.TEMP_SETTINGS['CYCLE_DELAY']:
                    await self._state_manager.transition(STATE_CYCLE_DELAY)
                    return
                    
                # Only attempt to turn on if cycle delay has elapsed
                if time_since_off >= self.config.TEMP_SETTINGS['CYCLE_DELAY'] and \
                   self._current_temp <= setpoint - self.config.TEMP_SETTINGS['TEMP_DIFFERENTIAL']:
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
            "setpoint": self.config.TEMP_SETTINGS['SETPOINT'],
            "timestamp": self._last_on_time
        })
        
    async def _turn_off(self):
        """Turn heater off"""
        await self.hardware.deactivate()
        self._last_off_time = time.time()
        await self.publish_event("heater_deactivated", {
            "temp": self._current_temp,
            "setpoint": self.config.TEMP_SETTINGS['SETPOINT'],
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
            
    async def reset_cycle_delay(self):
        """Reset cycle delay timing"""
        self._last_off_time = time.time()
        debug("Cycle delay timer reset") 
        
    async def _handle_timer_start(self, event):
        """Handle timer start event"""
        if event['action'] == "enable":
            debug(f"Timer start event received - enabling heater")
            await self.enable_heater()
            
    async def _handle_timer_end(self, event):
        """Handle timer end event"""
        if event['action'] == "disable":
            debug(f"Timer end event received - disabling heater")
            await self.disable_heater() 
        
    @property
    def heater_enabled(self):
        return self.config.TEMP_SETTINGS['HEATER_MODE'] == 'heat'
        
    @property
    def _cycle_delay(self):
        return self.config.TEMP_SETTINGS['CYCLE_DELAY']
        
    @property
    def _min_run_time(self):
        return self.config.TEMP_SETTINGS['MIN_RUN_TIME']
        
    @property
    def setpoint(self):
        return self.config.TEMP_SETTINGS['SETPOINT'] 