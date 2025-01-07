from .IoTController import IoTController
from .logging.Log import info
import asyncio

class DebugInterface:
    def __init__(self):
        self.controller = IoTController()
        
    async def start(self):
        """Initialize and start the system"""
        if not await self.controller.initialize():
            print("Failed to initialize system")
            return False
            
        print("\nDebug Interface Ready")
        print("Commands:")
        print("  temp - Show current temperature")
        print("  set <temp> - Set thermostat (e.g. 'set 72')")
        print("  heat on/off - Force heater state")
        print("  status - Show system status")
        print("  quit - Exit")
        
        while True:
            cmd = input("\nEnter command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "temp":
                temp_controller = self.controller.get_device("temperature")
                if temp_controller:
                    temp = await temp_controller.hardware.get_fahrenheit()
                    print(f"Current temperature: {temp}°F")
            elif cmd.startswith("set "):
                try:
                    temp = float(cmd.split()[1])
                    thermostat = self.controller.get_device("thermostat")
                    if thermostat:
                        if await thermostat.set_temperature(temp):
                            print(f"Setpoint changed to {temp}°F")
                        else:
                            print("Failed to set temperature")
                except (IndexError, ValueError):
                    print("Invalid temperature")
            elif cmd == "status":
                await self._show_status()
            elif cmd in ["heat on", "heat off"]:
                thermostat = self.controller.get_device("thermostat")
                if thermostat:
                    if cmd == "heat on":
                        await thermostat.hardware.activate()
                        print("Heater activated")
                    else:
                        await thermostat.hardware.deactivate()
                        print("Heater deactivated")
            else:
                print("Unknown command")
                
    async def _show_status(self):
        """Display current system status"""
        temp_controller = self.controller.get_device("temperature")
        thermostat = self.controller.get_device("thermostat")
        
        if temp_controller:
            temp = await temp_controller.hardware.get_fahrenheit()
            print(f"Temperature: {temp}°F")
            
        if thermostat:
            print(f"Setpoint: {thermostat.setpoint}°F")
            is_active = await thermostat.hardware.is_active()
            print(f"Heater: {'ON' if is_active else 'OFF'}") 