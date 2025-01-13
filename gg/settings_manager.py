# settings_manager.py
from config import SystemConfig
from gg.logging.Log import debug, error, info
import time

class SettingsManager:
    def __init__(self, events, logger):
        self.events = events
        self.logger = logger
        self.config = SystemConfig.get_instance()
        self.events.subscribe("thermostat_set_setpoint", self._handle_setpoint_change)
        self.events.subscribe("thermostat_set_cycle_delay", self._handle_cycle_delay_change)
        
    async def restore_all_settings(self):
        """Restore all settings on boot"""
        await self._restore_thermostat_state()
        # Add other settings restore methods
        
    async def _restore_thermostat_state(self):
        """Restore thermostat state from persistent storage.
        
        Returns:
            bool: True if state was successfully restored, False otherwise
        """
        try:
            thermostat_setpoint = self.logger.load_state(state_file="thermostat_setpoint.json")
            if not thermostat_setpoint:
                debug("No saved thermostat state found")
                return False
                
            # Validate required fields
            required_fields = {'setpoint', 'timestamp'}
            if not all(field in thermostat_setpoint for field in required_fields):
                error("Invalid thermostat state format - missing required fields")
                return False
                
            # Validate data types
            if not isinstance(thermostat_setpoint['setpoint'], (int, float)):
                error("Invalid setpoint type in saved state")
                return False
                
            if not isinstance(thermostat_setpoint['timestamp'], (int, float)):
                error("Invalid timestamp type in saved state")
                return False
                
            # Publish validated state
            await self.events.publish("thermostat_set_setpoint", {
                "setpoint": thermostat_setpoint['setpoint'],
                "timestamp": thermostat_setpoint['timestamp']
            })
            
            debug(f"Restored thermostat setpoint: {thermostat_setpoint['setpoint']}°F")
            return True
            
        except Exception as e:
            error(f"Failed to restore thermostat state: {e}")
            return False

    async def _handle_setpoint_change(self, event):
        """Handle thermostat setpoint changes"""
        # Save to persistent storage
        self.logger.save_state(event, state_file="thermostat_setpoint.json")
        
        # Update config directly
        config = SystemConfig.get_instance()
        success, old_value = config.update_setting('TEMP_SETTINGS', 'SETPOINT', event['setpoint'])
        
        if success:
            info(f"Thermostat setpoint changed from {old_value}°F to {event['setpoint']}°F")
        else:
            error(f"Failed to update thermostat setpoint to {event['setpoint']}°F")

    async def _handle_cycle_delay_change(self, event):
        """Handle thermostat cycle delay changes"""
        try:
            delay = event['delay']
            
            # Validate
            if delay < 0:
                error("Invalid cycle delay value")
                return False
                
            # Update config and persist
            success, old_value = self.config.update_setting('TEMP_SETTINGS', 'CYCLE_DELAY', delay)
            if success:
                self.logger.save_state({
                    'cycle_delay': delay,
                    'timestamp': time.time()
                }, state_file="thermostat_cycle_delay.json")
                
                info(f"Cycle delay changed from {old_value}s to {delay}s")
                return True
            return False
            
        except Exception as e:
            error(f"Failed to update cycle delay: {e}")
            return False