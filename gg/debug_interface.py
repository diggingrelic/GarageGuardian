import _thread
import asyncio
import time
from gg.logging.Log import debug, error

class DebugInterface:
    def __init__(self, controller):
        """Initialize debug interface with IoT controller"""
        self.controller = controller
        self.running = True
        self.command_queue = []
        self._lock = _thread.allocate_lock()
        
    async def _show_status(self):
        """Display system status"""
        debug("\nSystem Status:")
        
        # Temperature status
        temp_controller = self.controller.get_device("temperature")
        if temp_controller:
            temp = temp_controller.hardware.get_fahrenheit()
            debug(f"Current temperature: {temp}°F")
        else:
            debug("Temperature controller not found!")
            
        # Thermostat status
        thermostat = self.controller.get_device("thermostat")
        if thermostat:
            debug(f"Setpoint: {thermostat.setpoint}°F")
            debug(f"Heater enabled: {thermostat.heater_enabled}")
            debug(f"Heater active: {await thermostat.hardware.is_active()}")
            debug(f"Cycle delay: {thermostat._cycle_delay}s")
            debug(f"Min run time: {thermostat._min_run_time}s")
        else:
            debug("Thermostat controller not found!")

    async def start(self):
        """Initialize and start the debug interface"""
        debug("\nDebug Interface Ready")
        debug("Commands:")
        debug("  temp - Show current temperature")
        debug("  set <temp> - Set thermostat (e.g. 'set 72')")
        debug("  delay <seconds> - Set cycle delay")
        debug("  heat on/off - Force heater state")
        debug("  status - Show system status")
        debug("  hwtest - Run hardware integration tests")
        debug("  quit - Exit")

        # Start input thread (unchanged)
        _thread.start_new_thread(self._read_input, ())

        # Process commands in async loop (unchanged)
        while self.running:
            cmd = None
            with self._lock:
                if self.command_queue:
                    cmd = self.command_queue.pop(0)

            if cmd:
                try:
                    await self._handle_command(cmd)
                except Exception as e:
                    debug(f"Command error: {e}")

            await asyncio.sleep_ms(100)

    def _read_input(self):
        """Read user input in separate thread (unchanged)"""
        while self.running:
            try:
                cmd = input()
                with self._lock:
                    self.command_queue.append(cmd)
            except Exception as e:
                debug(f"Input error: {e}")
                time.sleep(1)

    async def _handle_command(self, cmd):
        """Handle a debug command"""
        try:
            cmd = cmd.strip().lower()
            debug(f"Processing command: {cmd}")

            if cmd == "quit":
                self.running = False
            elif cmd == "status":
                await self._show_status()
            elif cmd == "temp":
                temp_controller = self.controller.get_device("temperature")
                if temp_controller:
                    temp = temp_controller.hardware.get_fahrenheit()
                    debug(f"Current temperature: {temp}°F")
                else:
                    debug("Temperature controller not found!")
            elif cmd.startswith("set "):
                try:
                    temp = float(cmd.split()[1])
                    thermostat = self.controller.get_device("thermostat")
                    if thermostat:
                        if await thermostat.set_temperature(temp):
                            debug(f"Setpoint set to {temp}°F")
                        else:
                            debug("Failed to set temperature")
                    else:
                        debug("Thermostat controller not found!")
                except (ValueError, IndexError):
                    debug("Invalid temperature - use 'set <temp>'")
            elif cmd.startswith("delay "):
                try:
                    delay = int(cmd.split()[1])
                    await self.controller.update_system_setting('TEMP_SETTINGS', 'CYCLE_DELAY', delay)
                except (ValueError, IndexError):
                    debug("Invalid delay - use 'delay <seconds>'")
            elif cmd.startswith("heat "):
                state = cmd.split()[1]
                thermostat = self.controller.get_device("thermostat")
                if thermostat:
                    if state == "on":
                        if await thermostat.enable_heater():
                            debug("Heater control enabled")
                        else:
                            debug("Failed to enable heater control")
                    elif state == "off":
                        await thermostat.disable_heater()
                        debug("Heater control disabled")
                    else:
                        debug("Invalid state - use 'on' or 'off'")
                else:
                    debug("Thermostat controller not found!")
            elif cmd == "hwtest":
                debug("Starting hardware integration tests...")
                try:
                    from .testing.hardware_tests.run_hardware_tests import run_tests
                    passed, failed = await run_tests(self.controller)
                    if failed > 0:
                        error(f"Warning: {failed} tests failed!")
                    else:
                        debug("All hardware tests passed!")
                except Exception as e:
                    error(f"Hardware test error: {e}")
        except Exception as e:
            debug(f"Command error: {e}")