import asyncio
import time
from ..microtest import TestCase
from ...logging.Log import debug, error

class TestThermostatSystem(TestCase):
    def __init__(self, controller, settings_manager):
        """Initialize the test case"""
        super().__init__()
        self.controller = controller
        self.settings = settings_manager
        self.thermostat = None
        self.bmp390_service = None
        
    async def setUp(self):
        """Initialize test components"""
        # Get existing controllers from IoT controller
        self.thermostat = self.controller.get_device("thermostat")
        self.bmp390 = self.controller.get_service("bmp390")
        
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
            current_temp = self.bmp390.get_fahrenheit()
            debug(f"Current temperature: {current_temp}°F")
            
            # Set test parameters through IoT controller
            test_delay = 15
            min_run = 30
            
            debug(f"Setting cycle delay to {test_delay} seconds")
            await self.controller.events.publish("thermostat_set_cycle_delay", {
                "delay": test_delay,
                "timestamp": time.time()
            })

            await self.controller.events.publish("thermostat_set_min_run_time", {
                "min_run_time": min_run,
                "timestamp": time.time()
            })
            
            # Reset cycle delay timer before starting test
            await self.thermostat.reset_cycle_delay()
            
            debug("Setting setpoint to 90°F (above room temp)")
            await self.controller.events.publish("thermostat_set_setpoint", {
                "setpoint": 90,
                "timestamp": time.time()
            })
            
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
            
        except Exception as e:
            error(f"Test failed: {e}")
            raise

    async def test_timed_heating(self):
        """Test timed heating operation"""
        debug("=== Testing Timed Heating ===")
        
        try:
            # Reset cycle delay before starting
            await self.thermostat.reset_cycle_delay()
            
            # Set test parameters
            test_delay = 15
            test_duration_hours = 1/120  # 30 seconds in hours
            
            debug(f"Setting cycle delay to {test_delay} seconds")
            await self.controller.events.publish("thermostat_set_cycle_delay", {
                "delay": test_delay,
                "timestamp": time.time()
            })
            
            debug(f"Starting {test_duration_hours * 3600} second timed heat")
            result = await self.controller.start_timed_heat(test_duration_hours)
            self.assertTrue(result, "Failed to start timed heating")
            
            # Initially heater should be off (cycle delay)
            self.assertFalse(await self.thermostat.hardware.is_active(),
                           "Heater should be inactive during cycle delay")
            
            # Wait for cycle delay
            debug("Waiting for cycle delay...")
            await asyncio.sleep(test_delay + 1)
            
            # Now heater should be on
            self.assertTrue(await self.thermostat.hardware.is_active(),
                          "Heater should activate after cycle delay")
            
            # Wait for timer duration (minus cycle delay time)
            remaining_time = (test_duration_hours * 3600) - test_delay
            debug(f"Waiting {remaining_time} seconds for timer to complete...")
            await asyncio.sleep(remaining_time)
            
            # Verify heater stays on for minimum run time
            self.assertTrue(await self.thermostat.hardware.is_active(),
                          "Heater should stay on for minimum run time")
            
            # Wait for minimum run time
            await asyncio.sleep(test_delay)
            
            # Now heater should be off
            self.assertFalse(await self.thermostat.hardware.is_active(),
                           "Heater should turn off after minimum run time")
            
            debug("Test completed successfully!")
            
        except Exception as e:
            error(f"Timed heating test failed: {e}")
            raise

