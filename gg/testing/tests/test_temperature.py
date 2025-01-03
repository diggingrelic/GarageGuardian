from ..microtest import TestCase
from ...controllers.Temperature import TemperatureController
from ...core.Events import EventSystem
from ...core.Safety import SafetyMonitor
from ..mocks.MockTemperature import MockTemperature
import gc

class TestTemperatureController(TestCase):
    def setUp(self):
        self.hardware = MockTemperature()
        self.events = EventSystem()
        self.safety = SafetyMonitor()
        self.controller = TemperatureController("temp", self.hardware, self.safety, self.events)
        
    def tearDown(self):
        self.controller = None
        self.hardware = None
        self.events = None
        self.safety = None
        gc.collect()
        
    async def test_initialization(self):
        result = await self.controller.initialize()
        self.assertTrue(result)
        self.assertTrue(self.controller.enabled)
        
    async def test_temperature_reading(self):
        await self.controller.initialize()
        await self.hardware.set_temperature(25.0)
        await self.hardware.set_humidity(60.0)
        temp, humidity = await self.controller.read_sensor()
        self.assertEqual(temp, 25.0)
        self.assertEqual(humidity, 60.0)
        
    async def test_safety_limits(self):
        await self.controller.initialize()
        self.safety.add_condition(
            "temp_safe",
            lambda: self.hardware._temperature < 30.0,
            self.safety.SAFETY_HIGH
        )
        await self.hardware.set_temperature(25.0)
        self.assertTrue(await self.safety.check_safety())
        await self.hardware.set_temperature(35.0)
        self.assertFalse(await self.safety.check_safety()) 