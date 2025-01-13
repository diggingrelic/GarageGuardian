import _thread
import asyncio
import time
from gg.logging.Log import debug, error
from .system_interface import SystemInterface

class DebugInterface:
    def __init__(self, events, settings_manager, controller):
        """Initialize debug interface with system dependencies"""
        self.gui_controller = SystemInterface(
            events=events,
            settings_manager=settings_manager,
            controller=controller
        )
        self.running = True
        self.command_queue = []
        self._lock = _thread.allocate_lock()
        
    async def _show_status(self):
        """Display system status"""
        try:
            status = await self.gui_controller.get_status()
            debug("System Status:")
            debug(f"RTC time: {status['rtc_time']}")
            debug(f"System time: {status['sys_time']}")
            debug(f"Formatted RTC time: {status['formatted_time']}")
            
            if status['current_temp'] is not None:
                debug(f"Current temperature: {status['current_temp']}°F")
            else:
                debug("Temperature controller not found!")
                
            if status.get('thermostat') is not None:
                debug(f"Setpoint: {status['setpoint']}°F")
                debug(f"Heater enabled: {status['heater_mode']}")
                debug(f"Heater active: {status['heater_active']}")
                debug(f"Cycle delay: {status['cycle_delay']}s")
                debug(f"Min run time: {status['min_run_time']}s")
            else:
                debug("Thermostat controller not found!")

            if status['timer_end_time']:
                debug(f"Timer end: {status['timer_end_time']}")
                debug(f"Timer active: {status['timer_remaining']/60:.1f} minutes remaining")
            else:
                debug("No active timer")
                
        except Exception as e:
            debug(f"Error showing status: {e}")

    async def start(self):
        """Initialize and start the debug interface"""
        debug("\nDebug Interface Ready")
        debug("Commands:")
        debug("  ls [path] - List files (default: /sd)")
        debug("  cat <file> - Display file contents")
        debug("  temp - Show current temperature")
        debug("  set <temp> - Set thermostat (e.g. 'set 72')")
        debug("  delay <seconds> - Set cycle delay")
        debug("  min_run_time <seconds> - Set min run time")
        debug("  temp_differential <degrees> - Set temp differential")
        debug("  heater_mode heat/off - Turn heater on/off")
        debug("  timer start [minutes] - Start timed heat (default 30s)")
        debug("  timer stop - Stop timed heat")
        debug("  status - Show system status")
        debug("  hwtest - Run hardware integration tests")
        debug("  quit - Exit")

        _thread.start_new_thread(self._read_input, ())

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
        
        debug("Debug interface stopped")

    def _read_input(self):
        """Read user input in separate thread"""
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
            elif cmd.startswith("min_run_time "):
                try:
                    min_run_time = int(cmd.split()[1])
                    await self.gui_controller.set_min_run_time(min_run_time)
                    debug(f"Min run time set to {min_run_time}s")
                except Exception as e:
                    debug(str(e))
            elif cmd.startswith("temp_differential "):
                try:
                    temp_differential = int(cmd.split()[1])
                    await self.gui_controller.set_temp_differential(temp_differential)
                    debug(f"Temp differential set to {temp_differential}°F")
                except Exception as e:
                    debug(str(e))
            elif cmd.startswith("heater_mode "):
                try:
                    heater_mode = cmd.split()[1]
                    await self.gui_controller.set_heater_mode(heater_mode)
                    debug(f"Heater mode set to {heater_mode}")
                except Exception as e:
                    debug(str(e))
            elif cmd.startswith("ls"):
                try:
                    path = cmd.split()[1] if len(cmd.split()) > 1 else "/sd"
                    files = await self.gui_controller.list_directory(path)
                    debug(f"\nContents of {path}:")
                    for f in files:
                        debug(f"  {f}")
                except Exception as e:
                    debug(f"Error listing directory: {e}")
            elif cmd.startswith("cat"):
                try:
                    filename = cmd.split()[1]
                    content = await self.gui_controller.read_file(filename)
                    debug(f"Contents of {filename}:")
                    debug(content)
                except Exception as e:
                    debug(f"Error reading file: {e}")
            elif cmd.startswith("timer "):
                try:
                    action = cmd.split()[1]
                    if action == "start":
                        try:
                            minutes = float(cmd.split()[2])
                        except IndexError:
                            minutes = 0.5  # 30 seconds
                        
                        await self.gui_controller.start_timer(minutes)
                        debug(f"Timer started for {minutes} minutes")
                    elif action == "stop":
                        await self.gui_controller.stop_timer()
                        debug("Timer stopped")
                    else:
                        debug("Invalid timer command - use 'timer start [minutes]' or 'timer stop'")
                except Exception as e:
                    debug(f"Timer command error: {e}")
            elif cmd == "status":
                await self._show_status()
            elif cmd == "temp":
                try:
                    temp = await self.gui_controller.get_temperature()
                    debug(f"Current temperature: {temp}°F")
                except Exception as e:
                    debug(str(e))
            elif cmd.startswith("set "):
                try:
                    temp = float(cmd.split()[1])
                    await self.gui_controller.set_setpoint(temp)
                    debug(f"Setpoint set to {temp}°F")
                except Exception as e:
                    debug(str(e))
            elif cmd.startswith("delay "):
                try:
                    delay = int(cmd.split()[1])
                    await self.gui_controller.set_cycle_delay(delay)
                    debug(f"Cycle delay set to {delay}s")
                except (ValueError, IndexError):
                    debug("Invalid delay - use 'delay <seconds>'")
            elif cmd.startswith("heat "):
                try:
                    state = cmd.split()[1]
                    if state in ['on', 'off']:
                        await self.gui_controller.set_heater(state == 'on')
                        debug(f"Heater control {'enabled' if state == 'on' else 'disabled'}")
                    else:
                        debug("Invalid state - use 'on' or 'off'")
                except Exception as e:
                    debug(str(e))
            elif cmd == "hwtest":
                debug("Starting hardware integration tests...")
                try:
                    result = await self.gui_controller.run_hardware_tests()
                    if result['failed'] > 0:
                        error(f"Warning: {result['failed']} tests failed!")
                    else:
                        debug("All hardware tests passed!")
                except Exception as e:
                    error(f"Hardware test error: {e}")
        except Exception as e:
            debug(f"Command error: {e}")