import _thread
import asyncio
import time
from gg.logging.Log import debug, error
import os

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
        
        # Time status
        rtc = self.controller.logger.rtc  # Get RTC from logger
        rtc_time = rtc.get_time()  # Get raw RTC time
        sys_time = time.time()     # Get system time
        debug(f"RTC time: {rtc_time}")
        debug(f"System time: {sys_time}")
        debug(f"Formatted RTC time: {rtc.get_formatted_datetime()}")
        
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

        # Timer status
        if self.controller.timer_end_time:
            remaining = self.controller.timer_end_time - time.time()
            if remaining > 0:
                debug(f"Timer end: {self.controller.timer_end_time}")
                debug(f"Current time: {time.time()}")
                debug(f"Raw remaining seconds: {remaining}")
                debug(f"Timer active: {remaining/60:.1f} minutes remaining")
            else:
                debug("Timer expired")
        else:
            debug("No active timer")

    async def start(self):
        """Initialize and start the debug interface"""
        debug("\nDebug Interface Ready")
        debug("Commands:")
        debug("  ls [path] - List files (default: /sd)")
        debug("  cat <file> - Display file contents")
        debug("  temp - Show current temperature")
        debug("  set <temp> - Set thermostat (e.g. 'set 72')")
        debug("  delay <seconds> - Set cycle delay")
        debug("  heat on/off - Force heater state")
        debug("  timer start [minutes] - Start timed heat (default 30s)")
        debug("  timer stop - Stop timed heat")
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
            elif cmd.startswith("ls"):
                # List files in a directory (default to /sd)
                try:
                    path = cmd.split()[1] if len(cmd.split()) > 1 else "/sd"
                    files = os.listdir(path)
                    debug(f"\nContents of {path}:")
                    for f in files:
                        debug(f"  {f}")
                except Exception as e:
                    debug(f"Error listing directory: {e}")
            elif cmd.startswith("cat"):
                # Display contents of a file
                try:
                    filename = cmd.split()[1]
                    # Add /sd/ prefix if not already present
                    if not filename.startswith('/sd/'):
                        filename = f'/sd/{filename}'
                    with open(filename, 'r') as f:
                        content = f.read()
                    debug(f"Contents of {filename}:")
                    debug(content)
                except Exception as e:
                    debug(f"Error reading file: {e}")
            elif cmd.startswith("timer "):
                try:
                    action = cmd.split()[1]
                    if action == "start":
                        # Get duration in minutes (default to 30 seconds for testing)
                        try:
                            minutes = float(cmd.split()[2])
                        except IndexError:
                            minutes = 0.5  # 30 seconds
                        
                        if await self.controller.start_timed_heat(minutes/60):  # Convert to hours
                            debug(f"Timer started for {minutes} minutes")
                        else:
                            debug("Failed to start timer")
                    elif action == "stop":
                        # Add stop timer functionality to controller if needed
                        await self.controller.stop_timed_heat()
                        debug("Timer stopped")
                    else:
                        debug("Invalid timer command - use 'timer start [minutes]' or 'timer stop'")
                except Exception as e:
                    debug(f"Timer command error: {e}")
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