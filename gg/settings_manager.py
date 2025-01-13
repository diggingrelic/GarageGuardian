# settings_manager.py
from config import SystemConfig
from gg.logging.Log import debug, error, info
import time

class SettingsManager:
    def __init__(self, events, logger):
        self.events = events
        self.logger = logger
        self.config = SystemConfig.get_instance()
        # Subscribe to all settings-related events
        self.events.subscribe("temp_setting_changed", self._handle_temp_setting_change)

    async def restore_all_settings(self):
        """Restore all temperature settings from persistent storage"""
        # Load all settings in sequence
        await self._restore_setpoint()
        await self._restore_cycle_delay()
        await self._restore_min_run_time()
        await self._restore_temp_differential()
        await self._restore_heater_mode()

    async def _restore_setpoint(self):
        """Restore thermostat setpoint"""
        try:
            state = self.logger.load_state(state_file="thermostat_setpoint.json")
            if not state:
                debug("No saved setpoint found")
                return False

            if 'setpoint' not in state or 'timestamp' not in state:
                error("Invalid setpoint state format")
                return False

            setpoint = state['setpoint']
            if not isinstance(setpoint, (int, float)) or not 50 <= float(setpoint) <= 90:
                error(f"Invalid setpoint value: {setpoint}")
                return False

            await self.events.publish("temp_setting_changed", {
                "setting": "SETPOINT",
                "value": setpoint,
                "timestamp": state['timestamp']
            })
            debug(f"Restored thermostat setpoint: {setpoint}°F")
            return True

        except Exception as e:
            error(f"Failed to restore setpoint: {e}")
            return False

    async def _restore_cycle_delay(self):
        """Restore cycle delay"""
        try:
            state = self.logger.load_state(state_file="thermostat_cycle_delay.json")
            if not state:
                debug("No saved cycle delay found")
                return False

            if 'cycle_delay' not in state or 'timestamp' not in state:
                error("Invalid cycle delay state format")
                return False

            delay = state['cycle_delay']
            if not isinstance(delay, (int, float)) or delay < 0:
                error(f"Invalid cycle delay value: {delay}")
                return False

            await self.events.publish("temp_setting_changed", {
                "setting": "CYCLE_DELAY",
                "value": delay,
                "timestamp": state['timestamp']
            })
            debug(f"Restored cycle delay: {delay}s")
            return True

        except Exception as e:
            error(f"Failed to restore cycle delay: {e}")
            return False

    async def _restore_min_run_time(self):
        """Restore minimum run time"""
        try:
            state = self.logger.load_state(state_file="thermostat_min_run_time.json")
            if not state:
                debug("No saved minimum run time found")
                return False

            if 'min_run_time' not in state or 'timestamp' not in state:
                error("Invalid minimum run time state format")
                return False

            min_run = state['min_run_time']
            if not isinstance(min_run, (int, float)) or min_run < 0:
                error(f"Invalid minimum run time value: {min_run}")
                return False

            await self.events.publish("temp_setting_changed", {
                "setting": "MIN_RUN_TIME",
                "value": min_run,
                "timestamp": state['timestamp']
            })
            debug(f"Restored minimum run time: {min_run}s")
            return True

        except Exception as e:
            error(f"Failed to restore minimum run time: {e}")
            return False

    async def _restore_temp_differential(self):
        """Restore temperature differential"""
        try:
            state = self.logger.load_state(state_file="thermostat_temp_differential.json")
            if not state:
                debug("No saved temperature differential found")
                return False

            if 'temp_differential' not in state or 'timestamp' not in state:
                error("Invalid temperature differential state format")
                return False

            differential = state['temp_differential']
            if not isinstance(differential, (int, float)) or differential <= 0:
                error(f"Invalid temperature differential value: {differential}")
                return False

            await self.events.publish("temp_setting_changed", {
                "setting": "TEMP_DIFFERENTIAL",
                "value": differential,
                "timestamp": state['timestamp']
            })
            debug(f"Restored temperature differential: {differential}°F")
            return True

        except Exception as e:
            error(f"Failed to restore temperature differential: {e}")
            return False

    async def _restore_heater_mode(self):
        """Restore heater mode"""
        try:
            state = self.logger.load_state(state_file="thermostat_heater_mode.json")
            if not state:
                debug("No saved heater mode found")
                return False

            if 'heater_mode' not in state or 'timestamp' not in state:
                error("Invalid heater mode state format")
                return False

            mode = state['heater_mode']
            if mode not in ['heat', 'off']:
                error(f"Invalid heater mode value: {mode}")
                return False

            await self.events.publish("temp_setting_changed", {
                "setting": "HEATER_MODE",
                "value": mode,
                "timestamp": state['timestamp']
            })
            debug(f"Restored heater mode: {mode}")
            return True

        except Exception as e:
            error(f"Failed to restore heater mode: {e}")
            return False

    async def _handle_temp_setting_change(self, event):
        """Handle temperature setting changes"""
        try:
            setting = event['setting']
            value = event['value']
            
            # Validate based on setting type
            if not self._validate_temp_setting(setting, value):
                error(f"Invalid {setting} value: {value}")
                return False

            # Update config
            success, old_value = self.config.update_setting('TEMP_SETTINGS', setting, value)
            if success:
                # Map setting names to their file storage keys
                setting_keys = {
                    'SETPOINT': 'setpoint',
                    'CYCLE_DELAY': 'cycle_delay',
                    'MIN_RUN_TIME': 'min_run_time',
                    'TEMP_DIFFERENTIAL': 'temp_differential',
                    'HEATER_MODE': 'heater_mode'
                }

                # Save to persistent storage
                file_key = setting_keys[setting].lower()
                self.logger.save_state({
                    file_key: value,
                    'timestamp': time.time()
                }, state_file=f"thermostat_{file_key}.json")

                # Log the change
                unit = '°F' if setting in ['SETPOINT', 'TEMP_DIFFERENTIAL'] else 's'
                unit = '' if setting == 'HEATER_MODE' else unit
                info(f"Temperature setting {setting} changed from {old_value}{unit} to {value}{unit}")
                return True

            error(f"Failed to update {setting} in config")
            return False
            
        except Exception as e:
            error(f"Failed to update temperature setting: {e}")
            return False

    def _validate_temp_setting(self, setting, value):
        """Validate temperature settings"""
        if setting == 'SETPOINT':
            return isinstance(value, (int, float)) and 50 <= float(value) <= 90
        elif setting == 'CYCLE_DELAY':
            return isinstance(value, (int, float)) and float(value) >= 0
        elif setting == 'MIN_RUN_TIME':
            return isinstance(value, (int, float)) and float(value) >= 0
        elif setting == 'TEMP_DIFFERENTIAL':
            return isinstance(value, (int, float)) and float(value) > 0
        elif setting == 'HEATER_MODE':
            return value in ['heat', 'off']
        return False

