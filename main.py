import time
import asyncio
from config import LogConfig

# Development mode identifier and safety delay
print("\n" + "="*40)
print("DEVELOPMENT MODE")
print("Starting tests...")
print("="*40 + "\n")

# Run tests first if debug is enabled
if LogConfig.DEBUG:
    try:
        # Direct import of run_tests
        from gg.testing.run_tests import run_tests
        passed, failed = run_tests()
        if failed > 0:
            print("\nWARNING: Some tests failed!")
            time.sleep(2)
    except ImportError as e:
        print(f"Test import error: {str(e)}")
    except Exception as e:
        print(f"Test error: {e}")
        time.sleep(2)

# Continue with normal startup
print("\nStarting GarageOS...")
try:
    from gg.IoTController import IoTController
except Exception as e:
    print(f"Import error: {e}")
    raise

class GarageOS:
    def __init__(self):
        self.name = "GarageOS"
        self.version = "1.0.0"
        try:
            self.controller = IoTController()
        except Exception as e:
            print(f"Controller init error: {e}")
            raise
        self.running = True

    async def startup(self):
        """Initialize and start the system"""
        print(f"Starting {self.name} v{self.version}")
        print("Initializing system components...")
        
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
                await self.controller.run()
                await asyncio.sleep_ms(100)
                
        except Exception as e:
            print(f"System error: {e}")
            await self.safe_shutdown()
        except KeyboardInterrupt:
            print("\nClean shutdown requested")
            await self.safe_shutdown()

    async def safe_shutdown(self):
        """Perform safe system shutdown"""
        print("Performing safe shutdown...")
        self.running = False
        try:
            await self.controller.safe_shutdown()
        except Exception as e:
            print(f"Shutdown error: {e}")

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

# Handle startup and errors
try:
    print("Starting main asyncio loop")
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nSystem shutdown requested")
except Exception as e:
    print(f"Fatal error: {e}")
finally:
    # Development-friendly shutdown
    print("\n" + "="*40)
    print("System stopped. Use Thonny's Stop/Restart")
    print("to return to development mode.")
    print("="*40 + "\n")
