from ..microtest import TestCase
from ...controllers.Door import DoorController
from ...hardware.MockHAL import MockDoor
from ...core.Safety import SafetyMonitor
from ...core.Events import EventSystem

class TestDoor(TestCase):
    def __init__(self):
        super().__init__()
        self.hardware = MockDoor()
        self.safety = SafetyMonitor()
        self.events = EventSystem()
        self.controller = DoorController(self.hardware, self.safety, self.events)
        
    async def test_initialization(self):
        """Test controller initialization"""
        result = await self.controller.initialize()
        self.assertTrue(result)
        self.assertTrue(self.controller.enabled)
        
    async def test_open_door(self):
        """Test door opening"""
        await self.controller.initialize()
        # Door should start closed
        self.assertTrue(self.hardware.is_fully_closed())
        
        # Open door
        result = await self.controller.open_door()
        self.assertTrue(result)
        self.assertTrue(self.hardware.is_fully_open())
        
    async def test_close_door(self):
        """Test door closing"""
        await self.controller.initialize()
        # First open the door
        await self.controller.open_door()
        self.assertTrue(self.hardware.is_fully_open())
        
        # Close door
        result = await self.controller.close_door()
        self.assertTrue(result)
        self.assertTrue(self.hardware.is_fully_closed())
        
    async def test_obstruction_handling(self):
        """Test obstruction detection"""
        await self.controller.initialize()
        # Simulate obstruction
        self.hardware.simulate_obstruction(True)
        
        # Try to close door
        result = await self.controller.close_door()
        self.assertFalse(result)
        self.assertTrue(self.hardware.is_obstructed())
        
        # Clear obstruction
        self.hardware.simulate_obstruction(False)
        result = await self.controller.close_door()
        self.assertTrue(result)
        
    async def test_safety_integration(self):
        """Test safety system integration"""
        await self.controller.initialize()
        # Simulate obstruction
        self.hardware.simulate_obstruction(True)
        
        # Check safety condition
        safety_check = await self.safety.check_safety()
        self.assertFalse(safety_check)
        
        # Clear obstruction
        self.hardware.simulate_obstruction(False)
        safety_check = await self.safety.check_safety()
        self.assertTrue(safety_check) 