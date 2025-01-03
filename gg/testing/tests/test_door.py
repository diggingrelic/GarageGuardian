from ..microtest import TestCase
from ...controllers.Door import DoorController
from ...core.Events import EventSystem
from ...core.Safety import SafetyMonitor
from ..mocks.MockDoor import MockDoor
import gc

class TestDoorController(TestCase):
    def setUp(self):
        self.hardware = MockDoor()
        self.events = EventSystem()
        self.safety = SafetyMonitor()
        self.controller = DoorController("door", self.hardware, self.safety, self.events)
        
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
        
    async def test_lock_door(self):
        await self.controller.initialize()
        self.assertFalse(await self.hardware.is_locked())
        result = await self.controller.lock()
        self.assertTrue(result)
        self.assertTrue(await self.hardware.is_locked())
        
    async def test_unlock_door(self):
        await self.controller.initialize()
        await self.controller.lock()
        self.assertTrue(await self.hardware.is_locked())
        result = await self.controller.unlock()
        self.assertTrue(result)
        self.assertFalse(await self.hardware.is_locked())
        
    async def test_safety_check(self):
        """Test safety integration"""
        await self.controller.initialize()
        
        # Add safety condition
        self.safety.add_condition(
            "door_safe",
            lambda: not self.hardware.is_open(),
            self.safety.SAFETY_HIGH
        )
        
        # Try to lock when open (should fail)
        self.hardware.simulate_open()
        result = await self.controller.lock()
        self.assertFalse(result)
        self.assertFalse(self.hardware.is_locked()) 