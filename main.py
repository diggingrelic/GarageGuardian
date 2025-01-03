import time
import asyncio
from config import LogConfig
from gg.logging.Log import debug, info, warning, error, critical

# Development mode identifier
debug("=" * 40)
debug("DEVELOPMENT MODE")
debug("=" * 40)

# Run tests if enabled
if LogConfig.RUN_TESTS:
    try:
        from gg.testing.run_tests import run_tests
        passed, failed = run_tests()
        if failed > 0:
            warning("Some tests failed!")
            time.sleep(LogConfig.TEST_DELAY)
    except Exception as e:
        error(f"Test error: {e}")
        time.sleep(LogConfig.TEST_DELAY)
    debug("=" * 40)

# Start normal operation
try:
    from gg.IoTController import IoTController
except Exception as e:
    error(f"Import error: {e}")
    raise

class GarageOS:
    def __init__(self):
        self.name = "GarageOS"
        self.version = "1.0.0"
        try:
            self.controller = IoTController()
        except Exception as e:
            error(f"Controller init error: {e}")
            raise
        self.running = True

    async def startup(self):
        """Initialize and start the system"""
        info(f"Starting {self.name} v{self.version}")
        info("Initializing system components...")
        
        try:
            if await self.controller.initialize():
                info("System initialization successful")
                return True
            else:
                critical("System initialization failed - system cannot operate safely")
                return False
                
        except Exception as e:
            critical(f"Fatal startup error: {e}")
            return False

    async def run(self):
        """Main system run loop"""
        info("Entering main run loop...")
        try:
            while self.running:
                await self.controller.run()
                await asyncio.sleep_ms(100)
                
        except Exception as e:
            critical(f"Fatal system error: {e}")
            await self.safe_shutdown()
        except KeyboardInterrupt:
            info("\nClean shutdown requested")
            await self.safe_shutdown()

    async def safe_shutdown(self):
        """Perform safe system shutdown"""
        warning("Performing safe shutdown...")
        self.running = False
        try:
            await self.controller.safe_shutdown()
        except Exception as e:
            error(f"Shutdown error: {e}")

# Main execution
async def main():
    info("Initializing GarageOS...")
    try:
        system = GarageOS()
        
        if await system.startup():
            info("System ready, starting main loop")
            await system.run()
        else:
            info("System startup failed")
            await system.safe_shutdown()
    except Exception as e:
        error(f"Main error: {e}")

# Handle startup and errors
try:
    info("Starting main asyncio loop")
    asyncio.run(main())
except KeyboardInterrupt:
    info("\nSystem shutdown requested")
except Exception as e:
    error(f"Fatal error: {e}")
finally:
    # Development-friendly shutdown
    info("\n" + "="*40)
    info("System stopped. Use Thonny's Stop/Restart")
    info("to return to development mode.")
    info("="*40 + "\n")
