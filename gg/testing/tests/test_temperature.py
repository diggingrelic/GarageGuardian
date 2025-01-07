from ..microtest import TestCase
from ...controllers.Temperature import TemperatureController
from ...core.Events import EventSystem
from ...core.Safety import SafetyMonitor
from ..mocks.MockTemperature import MockTemperature
from ...config import SystemConfig
import gc
import time

class TestTemperatureController(TestCase):
    def setUp(self):
        self.events = EventSystem()
        self.safety = SafetyMonitor()
        self.hardware = MockTemperature()
        self.controller = TemperatureController("temp", self.hardware, self.safety, self.events)
        
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
        
    async def test_temperature_monitoring(self):
        """Test temperature monitoring and event publishing"""
        await self.controller.initialize()
        
        # Track published events
        temp_events = []
        change_events = []
        
        def on_current(data):
            temp_events.append(data)
            
        def on_change(data):
            change_events.append(data)
            
        self.events.subscribe("temperature_current", on_current)
        self.events.subscribe("temperature_changed", on_change)
        
        # Set initial temperature
        await self.hardware.set_temperature(70.0)
        await self.controller.monitor()
        
        # Should have one current and one change event
        self.assertEqual(len(temp_events), 1)
        self.assertEqual(len(change_events), 1)
        self.assertEqual(temp_events[0]["temp"], 70.0)
        
        # Set temperature within differential (shouldn't trigger change)
        small_change = 70.0 + (SystemConfig.TEMP_SETTINGS['TEMP_DIFFERENTIAL'] * 0.5)
        await self.hardware.set_temperature(small_change)
        await self.controller.monitor()
        
        # Should have new current but no new change event
        self.assertEqual(len(temp_events), 2)
        self.assertEqual(len(change_events), 1)
        
        # Set temperature outside differential
        big_change = 70.0 + (SystemConfig.TEMP_SETTINGS['TEMP_DIFFERENTIAL'] * 2)
        await self.hardware.set_temperature(big_change)
        await self.controller.monitor()
        
        # Should have both new current and change events
        self.assertEqual(len(temp_events), 3)
        self.assertEqual(len(change_events), 2)
        
    async def test_error_handling(self):
        """Test error handling for failed readings"""
        await self.controller.initialize()
        
        # Track error events
        errors = []
        def on_error(data):
            errors.append(data)
            
        self.events.subscribe("error", on_error)
        
        # Simulate sensor failure
        await self.hardware.simulate_error()
        await self.controller.monitor()
        
        self.assertTrue(len(errors) > 0) 