from ..microtest import TestCase
from ...core.Events import EventSystem
from ...core.Safety import SafetyMonitor
from ...controllers.Thermostat import ThermostatController
from ...devices.HeaterRelay import HeaterRelay
from config import SystemConfig
import gc
import time

class MockRelay(HeaterRelay):
    """Mock relay for testing"""
    def __init__(self):
        self.active = False
        
    async def activate(self):
        self.active = True
        
    async def deactivate(self):
        self.active = False
        
    async def is_active(self):
        return self.active

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
        
    async def test_heater_enable_disable(self):
        """Test heater enable/disable functionality"""
        await self.controller.initialize()
        await self.controller.set_temperature(72.0)
        
        # Initially disabled
        self.assertFalse(self.controller.heater_enabled)
        
        # Simulate cold temperature - should not turn on when disabled
        await self.controller.handle_temperature({
            "temp": 70.0,
            "timestamp": time.time()
        })
        self.assertFalse(await self.hardware.is_active())
        
        # Enable heater
        await self.controller.enable_heater()
        self.assertTrue(self.controller.heater_enabled)
        
        # Now should respond to temperature
        await self.controller.handle_temperature({
            "temp": 70.0,
            "timestamp": time.time()
        })
        self.assertTrue(await self.hardware.is_active())
        
        # Disable heater
        await self.controller.disable_heater()
        self.assertFalse(self.controller.heater_enabled)
        self.assertFalse(await self.hardware.is_active())
        
    async def test_cycle_delay_after_disable(self):
        """Test cycle delay is enforced after disable/enable"""
        await self.controller.initialize()
        await self.controller.set_temperature(72.0)
        await self.controller.enable_heater()
        
        # Turn on then disable
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        self.assertTrue(await self.hardware.is_active())
        
        await self.controller.disable_heater()
        self.assertFalse(await self.hardware.is_active())
        
        # Enable before cycle delay expires
        await self.controller.enable_heater()
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        self.assertFalse(await self.hardware.is_active())  # Should respect cycle delay
        
        # Wait for cycle delay
        time.sleep(SystemConfig.TEMP_SETTINGS['CYCLE_DELAY'])
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        self.assertTrue(await self.hardware.is_active())
        
    async def test_min_run_time_with_disable(self):
        """Test minimum run time is enforced even when disabling"""
        await self.controller.initialize()
        await self.controller.set_temperature(72.0)
        await self.controller.enable_heater()
        
        # Turn on heater
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        start_time = time.time()
        self.assertTrue(await self.hardware.is_active())
        
        # Try to disable before minimum run time
        await self.controller.disable_heater()
        self.assertFalse(self.controller.heater_enabled)
        self.assertTrue(await self.hardware.is_active())  # Should stay on until min run time
        
        # Wait for minimum run time
        remaining_time = (start_time + SystemConfig.TEMP_SETTINGS['MIN_RUN_TIME']) - time.time()
        if remaining_time > 0:
            time.sleep(remaining_time)
            
        # Now should turn off
        await self.controller.handle_temperature({"temp": 70.0, "timestamp": time.time()})
        self.assertFalse(await self.hardware.is_active()) 