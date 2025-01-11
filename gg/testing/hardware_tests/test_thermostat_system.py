import asyncio
import time
from ..microtest import TestCase
from ...logging.Log import debug, error
from config import SystemConfig

class TestThermostatSystem(TestCase):
    def __init__(self, controller):
        """Initialize the test case"""
        super().__init__()
        self.controller = controller
        self.thermostat = None
        self.temp_controller = None
        
    async def setUp(self):
        """Initialize test components"""
        # Get existing controllers from IoT controller
        self.thermostat = self.controller.get_device("thermostat")
        self.temp_controller = self.controller.get_device("temperature")
        
    async def tearDown(self):
        """Clean up after test"""
        if self.thermostat:
            await self.thermostat.hardware.deactivate()
            await asyncio.sleep(1)
        
    async def test_cycle_delay_enforcement(self):
        """Test cycle delay with real hardware"""
        debug("=== Testing Thermostat Cycle Delay ===")
        
        try:
            # Get current temperature
            current_temp = self.temp_controller.hardware.get_fahrenheit()
            debug(f"Current temperature: {current_temp}°F")
            
            # Set test parameters
            test_delay = 15
            min_run = 30  # 30 second minimum run time
            debug(f"Setting cycle delay to {test_delay} seconds")
            await self.thermostat.set_cycle_delay(test_delay)
            SystemConfig.TEMP_SETTINGS['MIN_RUN_TIME'] = min_run
            
            debug("Setting setpoint to 90°F (above room temp)")
            await self.thermostat.set_temperature(90.0)
            
            # Enable and monitor
            debug("Enabling heater and monitoring activation")
            start_time = time.time()
            await self.thermostat.enable_heater()
            
            # Wait for activation
            while time.time() - start_time < test_delay + 5:
                if await self.thermostat.hardware.is_active():
                    elapsed = time.time() - start_time
                    debug(f"Heater activated after {elapsed:.1f} seconds")
                    self.assertGreaterEqual(elapsed, test_delay)
                    break
                await asyncio.sleep(1)
            else:
                error("Heater failed to activate")
                self.assertTrue(False, "Heater failed to activate")
                
            # Immediately try to turn it off
            debug(f"Disabling heater (should stay on for {min_run}s minimum)")
            await self.thermostat.disable_heater()
            
            start_time = time.time()
            while await self.thermostat.hardware.is_active():
                elapsed = time.time() - start_time
                if elapsed > min_run + 5:
                    self.fail("Heater stayed on too long")
                await asyncio.sleep(1)
                if elapsed % 5 == 0:  # Only log every 5 seconds
                    debug(f"Still on after {elapsed:.1f}s")
                
            elapsed = time.time() - start_time
            debug(f"Heater deactivated after {elapsed:.1f} seconds")
            self.assertGreaterEqual(elapsed, min_run)
            
            debug("Test completed successfully!")
            
        finally:
            # Cleanup
            await self.thermostat.hardware.deactivate()
            await asyncio.sleep(1) 