# main.py - Production version with automatic recovery
import machine # type: ignore
import time
import asyncio

# No delay in production
print("PRODUCTION MODE")

# Import our GarageOS system
try:
    from gg.system_controller import SystemController
except Exception as e:
    print(f"Import error: {e}")
    machine.reset()  # In production, reset on import failure

class GarageOS:
    def __init__(self):
        self.name = "GarageOS"
        self.version = "1.0.0"
        self.watchdog = machine.WDT(timeout=8000)  # 8 second watchdog
        try:
            self.controller = SystemController()
        except Exception as e:
            print(f"Controller init error: {e}")
            machine.reset()
        self.running = True

    async def startup(self):
        """Initialize and start the system"""
        print(f"Starting {self.name} v{self.version}")
        self.watchdog.feed()
        
        try:
            if await self.controller.initialize():
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
        print("Entering main run loop...")
        try:
            while self.running:
                self.watchdog.feed()  # Feed watchdog in main loop
                await self.controller.run()
                await asyncio.sleep_ms(100)
                
        except Exception as e:
            print(f"System error: {e}")
            await self.safe_shutdown()

    async def safe_shutdown(self):
        """Perform safe system shutdown"""
        print("Performing safe shutdown...")
        self.running = False
        try:
            await self.controller.safe_shutdown()
        except Exception as e:
            print(f"Shutdown error: {e}")
        finally:
            machine.reset()  # Always reset in production

# Main execution
async def main():
    print("Initializing GarageOS...")
    try:
        system = GarageOS()
        
        if await system.startup():
            print("System ready, starting main loop")
            await system.run()
        else:
            print("System startup failed")
            await system.safe_shutdown()
    except Exception as e:
        print(f"Main error: {e}")
        machine.reset()

# Handle startup and errors
while True:  # Production infinite retry loop
    try:
        print("Starting main asyncio loop")
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}")
        time.sleep(5)  # Wait before retry
        machine.reset()