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
import time
import asyncio
from config import SystemConfig

class ThermostatController(BaseController):
    """Controls heater based on temperature events and settings"""
    
    def __init__(self, name, heater_relay, safety, events):
        super().__init__(name, heater_relay, safety, events)
        self.config = SystemConfig.get_instance()
        
        # Initialize settings from config
        self._setpoint = self.config.TEMP_SETTINGS['SETPOINT']
        self._cycle_delay = self.config.TEMP_SETTINGS['CYCLE_DELAY']
        self._min_run_time = self.config.TEMP_SETTINGS['MIN_RUN_TIME']
        self._temp_differential = self.config.TEMP_SETTINGS['TEMP_DIFFERENTIAL']
        self._heater_mode = 'off'
        
        # Non-persistent state
        self._last_off_time = time.time()
        self._last_on_time = 0
        self._current_temp = None
        self._state_manager = ThermostatStateManager(self)
        
        # Subscribe to events
        self.events.subscribe("temperature_current", self._handle_temperature)
        self.events.subscribe("thermostat_timer_start", self._handle_timer_start)
        self.events.subscribe("thermostat_timer_end", self._handle_timer_end)
        self.events.subscribe("temp_setting_changed", self._handle_setting_change)
        
    async def initialize(self):
        """Initialize the thermostat hardware"""
        await super().initialize()
        await self.hardware.deactivate()
        await self._state_manager.transition(STATE_IDLE)
        return True

    async def _handle_setting_change(self, event):
        """Handle settings changes from SettingsManager"""
        setting = event['setting']
        value = event['value']
        
        if setting == 'HEATER_MODE':
            self._heater_mode = value
            if value == 'off':
                await self._state_manager.transition(STATE_DISABLED)
            else:
                await self._state_manager.transition(STATE_IDLE)
        elif setting == 'SETPOINT':
            self._setpoint = float(value)
        elif setting == 'CYCLE_DELAY':
            self._cycle_delay = float(value)
        elif setting == 'MIN_RUN_TIME':
            self._min_run_time = float(value)
        elif setting == 'TEMP_DIFFERENTIAL':
            self._temp_differential = float(value)
            
        # Check if we need to update heater state
        await self._check_thermostat()
        
    async def _handle_temperature(self, data):
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
            
        await self.events.publish("temp_setting_changed", {
            "setting": "HEATER_MODE",
            "value": "heat",
            "timestamp": time.time()
        })
        return True
        
    async def disable_heater(self):
        """Disable heater control"""
        await self.events.publish("temp_setting_changed", {
            "setting": "HEATER_MODE",
            "value": "off",
            "timestamp": time.time()
        })
        
    async def _check_thermostat(self):
        """Check if heater should be on/off based on current temperature"""
        try:
            if not all([self._setpoint, self._cycle_delay, self._min_run_time, self._temp_differential]):
                debug("Not all settings initialized yet")
                return
                
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
                
            # If heater is on, check if it should turn off
            if await self.hardware.is_active():
                if self._current_temp >= self._setpoint + self._temp_differential:
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
                   self._current_temp <= self._setpoint - self._temp_differential:
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
            "setpoint": self._setpoint,
            "timestamp": self._last_on_time
        })
        
    async def _turn_off(self):
        """Turn heater off"""
        await self.hardware.deactivate()
        self._last_off_time = time.time()
        await self.publish_event("heater_deactivated", {
            "temp": self._current_temp,
            "setpoint": self._setpoint,
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
        """Is heater control enabled"""
        return self._heater_mode == 'heat'
        
    @property
    def heater_mode(self):
        """Current heater mode (heat/off)"""
        return self._heater_mode
        
    @property
    def setpoint(self):
        return self._setpoint
    
    @property
    def cycle_delay(self):
        return self._cycle_delay
    
    @property
    def min_run_time(self):
        return self._min_run_time
    
    @property
    def temp_differential(self):
        return self._temp_differential