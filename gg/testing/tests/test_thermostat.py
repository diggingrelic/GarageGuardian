from ..microtest import TestCase
from ...controllers.Thermostat import ThermostatController
from ...core.Events import EventSystem
from ...core.Safety import SafetyMonitor
from ..mocks.MockRelay import MockRelay
from ...config import SystemConfig
import gc
import time

class TestThermostatController(TestCase):
    def setUp(self):
        self.events = EventSystem()
        self.safety = SafetyMonitor()
        self.hardware = MockRelay()
        self.controller = ThermostatController("thermostat", self.hardware, self.safety, self.events)
        
    def tearDown(self):
        self.controller = None
        self.hardware = None
        self.events = None
        self.safety = None
        gc.collect()
        
    async def test_initialization(self):
        """Test controller initialization"""
        result = await self.controller.initialize()
        self.assertTrue(result)
        self.assertTrue(self.controller.enabled)
        self.assertFalse(await self.hardware.is_active())
        
    async def test_setpoint_control(self):
        """Test setpoint changes"""
        await self.controller.initialize()
        
        # Valid setpoint
        result = await self.controller.set_temperature(72.0)
        self.assertTrue(result)
        self.assertEqual(self.controller.setpoint, 72.0)
        
        # Invalid setpoint (too high)
        result = await self.controller.set_temperature(SystemConfig.TEMP_SETTINGS['MAX_TEMP'] + 1)
        self.assertFalse(result)
        self.assertEqual(self.controller.setpoint, 72.0)
        
    async def test_temperature_response(self):
        """Test thermostat response to temperature changes"""
        await self.controller.initialize()
        await self.controller.set_temperature(72.0)
        
        # Simulate cold temperature
        await self.controller.handle_temperature({
            "temp": 70.0,
            "timestamp": time.time()
        })
        
        # Should turn on
        self.assertTrue(await self.hardware.is_active())
        
        # Simulate warm temperature
        await self.controller.handle_temperature({
            "temp": 74.0,
            "timestamp": time.time()
        })
        
        # Should turn off after minimum run time
        time.sleep(SystemConfig.TEMP_SETTINGS['MIN_RUN_TIME'])
        await self.controller.handle_temperature({
            "temp": 74.0,
            "timestamp": time.time()
        })
        self.assertFalse(await self.hardware.is_active())
        
    async def test_cycle_delay(self):
        """Test cycle delay enforcement"""
        await self.controller.initialize()
        await self.controller.set_temperature(72.0)
        
        # Turn on then off
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        self.assertTrue(await self.hardware.is_active())
        
        await self.controller.handle_temperature({"temp": 74.0, "timestamp": time.time()})
        time.sleep(SystemConfig.TEMP_SETTINGS['MIN_RUN_TIME'])
        await self.controller.handle_temperature({"temp": 74.0, "timestamp": time.time()})
        self.assertFalse(await self.hardware.is_active())
        
        # Try to turn on before cycle delay
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        self.assertFalse(await self.hardware.is_active())
        
        # Wait for cycle delay
        time.sleep(SystemConfig.TEMP_SETTINGS['CYCLE_DELAY'])
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        self.assertTrue(await self.hardware.is_active()) 