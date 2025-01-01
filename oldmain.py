import machine
import time
import json
import asyncio
from collections import deque
from machine import Pin, I2C

# Import our GarageOS system
from gg.IoTController import IoTController

class GarageOS:
    def __init__(self):
        self.name = "GarageOS"
        self.version = "1.0.0"
        self.controller = IoTController()
        self.system_led = Pin(25, Pin.OUT)
        self.running = True

    async def startup(self):
        """Initialize and start the system"""
        print(f"Starting {self.name} v{self.version}")
        print("Initializing system components...")
        
        try:
            if await self.controller.initialize_system():
                print("System initialization successful")
                return True
            else:
                print("System initialization failed")
                return False
                
        except Exception as e:
            print(f"Startup error: {e}")
            return False

    async def run(self):
        """Main system run loop"""
        try:
            while self.running:
                self.system_led.toggle()  # Heartbeat
                await self.controller.run()
                await asyncio.sleep_ms(100)
                
        except Exception as e:
            print(f"System error: {e}")
            await self.safe_shutdown()

    async def safe_shutdown(self):
        """Perform safe system shutdown"""
        print("Performing safe shutdown...")
        self.running = False
        self.system_led.off()
        # Allow controller to perform cleanup
        await self.controller.safe_shutdown()

async def main():
    """Main application entry point"""
    try:
        # Create and start GarageOS
        system = GarageOS()
        
        if await system.startup():
            print("System ready")
            await system.run()
        else:
            print("System startup failed")
            await system.safe_shutdown()
            
    except KeyboardInterrupt:
        print("\nSystem shutdown requested")
        await system.safe_shutdown()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        machine.reset()
        
    finally:
        # Emergency cleanup
        machine.reset()

# Handle startup and errors
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEmergency shutdown initiated")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        # Ensure system resets in case of fatal error
        machine.reset()