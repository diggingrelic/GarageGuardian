import _thread
import asyncio
import time

class DebugInterface:
    def __init__(self, controller):
        """Initialize debug interface with IoT controller"""
        self.controller = controller
        self.running = True
        self.command_queue = []
        self._lock = _thread.allocate_lock()
        
    async def _show_status(self):
        """Show current system status"""
        try:
            temp_controller = self.controller.get_device("temperature")
            thermostat = self.controller.get_device("thermostat")
            
            if temp_controller and thermostat:
                temp = temp_controller.hardware.get_fahrenheit()
                print("\nCurrent Status:")
                print(f"Temperature: {temp}°F")
                print(f"Setpoint: {thermostat.setpoint}°F")
                print(f"Heater Enabled: {thermostat.heater_enabled}")
                print(f"Heater Active: {await thermostat.hardware.is_active()}")
            else:
                print("Temperature or thermostat controller not found!")
                
        except Exception as e:
            print(f"Error getting status: {e}")
            
    async def start(self):
        """Initialize and start the debug interface"""
        print("\nDebug Interface Ready")
        print("Commands:")
        print("  temp - Show current temperature")
        print("  set <temp> - Set thermostat (e.g. 'set 72')")
        print("  delay <seconds> - Set cycle delay")
        print("  heat on/off - Force heater state")
        print("  status - Show system status")
        print("  quit - Exit")

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
                    print(f"Command error: {e}")

            await asyncio.sleep_ms(100)

    def _read_input(self):
        """Read user input in separate thread (unchanged)"""
        while self.running:
            try:
                cmd = input()
                with self._lock:
                    self.command_queue.append(cmd)
            except Exception as e:
                print(f"Input error: {e}")
                time.sleep(1)

    async def _handle_command(self, cmd):
        """Handle a debug command"""
        try:
            cmd = cmd.strip().lower()
            print(f"\nProcessing command: {cmd}")

            if cmd == "quit":
                self.running = False
            elif cmd == "temp":
                temp_controller = self.controller.get_device("temperature")
                if temp_controller:
                    temp = temp_controller.hardware.get_fahrenheit()
                    print(f"Current temperature: {temp}°F")
                else:
                    print("Temperature controller not found!")
            elif cmd.startswith("set "):
                try:
                    temp = float(cmd.split()[1])
                    thermostat = self.controller.get_device("thermostat")
                    if thermostat:
                        if await thermostat.set_temperature(temp):
                            print(f"Setpoint set to {temp}°F")
                        else:
                            print("Failed to set temperature")
                    else:
                        print("Thermostat controller not found!")
                except (ValueError, IndexError):
                    print("Invalid temperature - use 'set <temp>'")
            elif cmd.startswith("delay "):
                try:
                    delay = int(cmd.split()[1])
                    thermostat = self.controller.get_device("thermostat")
                    if thermostat:
                        if await thermostat.set_cycle_delay(delay):
                            print(f"Cycle delay set to {delay} seconds")
                        else:
                            print("Failed to set cycle delay")
                    else:
                        print("Thermostat controller not found!")
                except (ValueError, IndexError):
                    print("Invalid delay - use 'delay <seconds>'")
            elif cmd.startswith("heat "):
                state = cmd.split()[1]
                thermostat = self.controller.get_device("thermostat")
                if thermostat:
                    if state == "on":
                        if await thermostat.enable_heater():
                            print("Heater control enabled")
                        else:
                            print("Failed to enable heater control")
                    elif state == "off":
                        await thermostat.disable_heater()
                        print("Heater control disabled")
                    else:
                        print("Invalid state - use 'on' or 'off'")
                else:
                    print("Thermostat controller not found!")
        except Exception as e:
            print(f"Command error: {e}")