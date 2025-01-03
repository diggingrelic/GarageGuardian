from ..microtest import TestCase
from ...controllers.Motion import MotionController
from ...core.Events import EventSystem
from ...core.Safety import SafetyMonitor
from ..mocks.MockMotion import MockMotion
import gc

class TestMotionController(TestCase):
    def setUp(self):
        self.hardware = MockMotion()
        self.events = EventSystem()
        self.safety = SafetyMonitor()
        self.controller = MotionController("motion", self.hardware, self.safety, self.events)
        
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
        
    async def test_motion_detection(self):
        await self.controller.initialize()
        self.assertFalse(await self.controller.check_motion())
        await self.hardware.simulate_motion()
        self.assertTrue(await self.controller.check_motion())
        await self.hardware.simulate_clear()
        self.assertFalse(await self.controller.check_motion())
        
    async def test_sensitivity_control(self):
        await self.controller.initialize()
        self.assertTrue(await self.controller.set_sensitivity(5))
        self.assertEqual(await self.controller.get_sensitivity(), 5)
        self.assertFalse(await self.controller.set_sensitivity(11))
        self.assertEqual(await self.controller.get_sensitivity(), 5) 