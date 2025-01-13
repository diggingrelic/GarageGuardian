import time
import os


class SystemInterface:
    """Debug controller that can be used by both terminal and UI interfaces"""
    def __init__(self, events, settings_manager, controller):
        self.events = events
        self.settings = settings_manager
        self.controller = controller
        
    async def get_status(self):
        """Get complete system status as a dictionary"""
        status = {}
        
        # Time status
        rtc = self.controller.logger.rtc
        status['rtc_time'] = rtc.get_time()
        status['sys_time'] = time.time()
        status['formatted_time'] = rtc.get_formatted_datetime()
        
        # Temperature status
        temp_controller = self.controller.get_device("temperature")
        if temp_controller:
            status['current_temp'] = temp_controller.hardware.get_fahrenheit()
        else:
            status['current_temp'] = None
            
        # Thermostat status
        thermostat = self.controller.get_device("thermostat")
        if thermostat:
            status['thermostat'] = True
            status['setpoint'] = thermostat.setpoint
            status['heater_enabled'] = thermostat.heater_enabled
            status['heater_active'] = await thermostat.hardware.is_active()
            status['cycle_delay'] = thermostat._cycle_delay
            status['min_run_time'] = thermostat._min_run_time
        else:
            status['thermostat'] = None
            
        # Timer status
        if self.controller.timer_end_time:
            remaining = self.controller.timer_end_time - time.time()
            status['timer_end_time'] = self.controller.timer_end_time
            status['timer_remaining'] = remaining if remaining > 0 else 0
        else:
            status['timer_end_time'] = None
            status['timer_remaining'] = None
            
        return status
        
    async def list_directory(self, path="/sd"):
        """List contents of directory"""
        try:
            return os.listdir(path)
        except Exception as e:
            raise Exception(f"Error listing directory: {e}")
            
    async def read_file(self, filename):
        """Read contents of a file"""
        try:
            if not filename.startswith('/sd/'):
                filename = f'/sd/{filename}'
            with open(filename, 'r') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
            
    async def start_timer(self, minutes=0.5):
        """Start timed heat"""
        success = await self.controller.start_timed_heat(minutes/60)
        if not success:
            raise Exception("Failed to start timer")
        return True
        
    async def stop_timer(self):
        """Stop timed heat"""
        await self.controller.stop_timed_heat()
        return True
        
    async def get_temperature(self):
        """Get current temperature"""
        temp_controller = self.controller.get_device("temperature")
        if temp_controller:
            return temp_controller.hardware.get_fahrenheit()
        raise Exception("Temperature controller not found!")
        
    async def set_setpoint(self, temp):
        """Set thermostat temperature"""
        await self.events.publish("thermostat_set_setpoint", {
            "setpoint": temp,
            "timestamp": time.time()
        })
        
    async def set_cycle_delay(self, delay):
        """Set cycle delay"""
        await self.events.publish("thermostat_set_cycle_delay", {
            "delay": delay,
            "timestamp": time.time()
        })
        
    async def set_heater(self, enabled):
        """Set heater state"""
        thermostat = self.controller.get_device("thermostat")
        if not thermostat:
            raise Exception("Thermostat controller not found!")
            
        if enabled:
            if not await thermostat.enable_heater():
                raise Exception("Failed to enable heater")
        else:
            await thermostat.disable_heater()
        return True
        
    async def run_hardware_tests(self):
        """Run hardware tests"""
        try:
            from .testing.hardware_tests.run_hardware_tests import run_tests
            passed, failed = await run_tests(self.controller)
            return {"passed": passed, "failed": failed}
        except Exception as e:
            raise Exception(f"Hardware test error: {e}")