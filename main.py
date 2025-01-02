import time
import asyncio
from config import LogConfig
from gg.logging.Log import log

# Development mode identifier
print("=" * 40)
print("DEVELOPMENT MODE")
print("=" * 40)

# Run tests if enabled
if LogConfig.RUN_TESTS:
    try:
        from gg.testing.run_tests import run_tests
        passed, failed = run_tests()
        if failed > 0:
            print("WARNING: Some tests failed!")
            time.sleep(LogConfig.TEST_DELAY)
    except Exception as e:
        print(f"Test error: {e}")
        time.sleep(LogConfig.TEST_DELAY)
    print("=" * 40)

# Start normal operation
log("\nStarting GarageOS...")
try:
    from gg.IoTController import IoTController
except Exception as e:
    log(f"Import error: {e}")
    raise

class GarageOS:
    def __init__(self):
        self.name = "GarageOS"
        self.version = "1.0.0"
        try:
            self.controller = IoTController()
        except Exception as e:
            log(f"Controller init error: {e}")
            raise
        self.running = True

    async def startup(self):
        """Initialize and start the system"""
        log(f"Starting {self.name} v{self.version}")
        log("Initializing system components...")
        
        try:
            if await self.controller.initialize():
                log("System initialization successful")
                return True
            else:
                log("System initialization failed")
                return False
                
        except Exception as e:
            log(f"Startup error: {e}")
            return False

    async def run(self):
        """Main system run loop"""
        log("Entering main run loop...")
        try:
            while self.running:
                await self.controller.run()
                await asyncio.sleep_ms(100)
                
        except Exception as e:
            log(f"System error: {e}")
            await self.safe_shutdown()
        except KeyboardInterrupt:
            log("\nClean shutdown requested")
            await self.safe_shutdown()

    async def safe_shutdown(self):
        """Perform safe system shutdown"""
        log("Performing safe shutdown...")
        self.running = False
        try:
            await self.controller.safe_shutdown()
        except Exception as e:
            log(f"Shutdown error: {e}")

# Main execution
async def main():
    log("Initializing GarageOS...")
    try:
        system = GarageOS()
        
        if await system.startup():
            log("System ready, starting main loop")
            await system.run()
        else:
            log("System startup failed")
            await system.safe_shutdown()
    except Exception as e:
        log(f"Main error: {e}")

# Handle startup and errors
try:
    log("Starting main asyncio loop")
    asyncio.run(main())
except KeyboardInterrupt:
    log("\nSystem shutdown requested")
except Exception as e:
    log(f"Fatal error: {e}")
finally:
    # Development-friendly shutdown
    log("\n" + "="*40)
    log("System stopped. Use Thonny's Stop/Restart")
    log("to return to development mode.")
    log("="*40 + "\n")
