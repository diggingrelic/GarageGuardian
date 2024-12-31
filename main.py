import machine
import time
import json
from collections import deque
import asyncio
from machine import Pin, I2C
from gg.IoTController import IoTController

class GarageOS:
    def __init__(self):
        self.name = "GarageOS"
        self.version = "1.0.0"
        self.controller = IoTController()
        self.i2c = I2C(0, scl=Pin(17), sda=Pin(16))
        self.system_led = Pin(25, Pin.OUT)
        
    async def startup(self):
        print(f"Starting {self.name} v{self.version}")
        print("Initializing system components...")
        
        if await self.controller.initialize_system():
            print("System initialization successful")
            return True
        return False
    
    async def run(self):
        try:
            while True:
                self.system_led.toggle()  # Heartbeat
                await self.controller.run()
                await asyncio.sleep_ms(100)
        except Exception as e:
            print(f"System error: {e}")
            await self.safe_shutdown()
            
    async def safe_shutdown(self):
        print("Performing safe shutdown...")
        # Shutdown sequence here
        self.system_led.off()

async def main():
    system = GarageOS()
    
    if await system.startup():
        print("System ready")
        await system.run()
    else:
        print("System startup failed")
        await system.safe_shutdown()

# Handle startup and errors
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nSystem shutdown requested")
except Exception as e:
    print(f"Fatal error: {e}")
finally:
    # Emergency cleanup
    machine.reset()