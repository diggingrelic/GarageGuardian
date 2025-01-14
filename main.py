import time
import asyncio
from config import LogConfig
from gg.logging.Log import debug, info, warning, error, critical
from gg.debug_interface import DebugInterface
from gg.system_controller import SystemController
from gg.core.DeviceFactory import DeviceFactory
from gg.core.Events import EventSystem
from gg.core.Safety import SafetyMonitor
from gg.logging.file_logger import SimpleLogger
from gg.system_interface import SystemInterface
from gg.settings_manager import SettingsManager

# Initialize core logging first
logger = SimpleLogger.get_instance()

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

class GarageOS:
    def __init__(self):
        self.name = "GarageOS"
        self.version = "1.0.0"
        try:
            # Create core systems first
            self.logger = SimpleLogger.get_instance()
            self.events = EventSystem()
            self.safety = SafetyMonitor()
            
            # Create settings manager (needs events and logger)
            self.settings = SettingsManager(self.events, self.logger)
            
            # Create device factory
            self.device_factory = DeviceFactory()
            
            # Initialize main controller with dependencies
            self.controller = SystemController(
                event_system=self.events,
                safety_monitor=self.safety,
                settings_manager=self.settings  # Pass settings manager in
            )
            
            # Create system interface last since it needs everything
            self.interface = SystemInterface(
                self.events,
                self.settings,
                self.controller  # For device access
            )

            '''
            # Create core systems
            self.events = EventSystem()
            self.safety = SafetyMonitor()
            self.device_factory = DeviceFactory()
            
            # Initialize controller with dependencies
            self.controller = SystemController(
                event_system=self.events,
                safety_monitor=self.safety
            )
            '''
        except Exception as e:
            error(f"Controller init error: {e}")
            raise
        self.running = True

    async def startup(self):
        """Initialize and start the system"""
        info(f"Starting {self.name} v{self.version}")
        info("Initializing system components...")
        
        try:
            if await self.controller.initialize(device_factory=self.device_factory):
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

async def main():
    info("Initializing GarageOS...")
    try:
        system = GarageOS()
        
        if await system.startup():
            info("System ready, starting main loop")
            # Create debug interface with existing system controller
            interface = DebugInterface(
                events=system.events,
                settings_manager=system.settings,
                controller=system.controller
            )
            
            # Create tasks for both system and debug interface
            system_task = asyncio.create_task(system.run())
            interface_task = asyncio.create_task(interface.start())
            
            # Wait for either task to complete
            await asyncio.gather(system_task, interface_task)
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
    # Close logger on shutdown
    logger.close()
