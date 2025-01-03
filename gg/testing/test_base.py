from .microtest import TestCase
from ..controllers.Base import BaseController
from .mocks import MockPin
from ..core.Safety import SafetyMonitor
from ..core.Events import EventSystem

class TestBaseController(TestCase):
    def __init__(self):
        super().__init__()
        self.hardware = MockPin("TEST", MockPin.OUT)
        self.safety = SafetyMonitor()
        self.events = EventSystem()
        self.controller = BaseController("test", self.hardware, self.safety, self.events)
        
    async def test_initialization(self):
        """Test basic initialization"""
        result = await self.controller.initialize()
        self.assertTrue(result)
        self.assertTrue(self.controller.enabled)
        self.assertEqual(self.controller.name, "test")
        
    def test_attributes(self):
        """Test controller attributes"""
        self.assertEqual(self.controller.hardware, self.hardware)
        self.assertEqual(self.controller.safety, self.safety)
        self.assertEqual(self.controller.events, self.events)
        
    async def test_update(self):
        """Test update method (should do nothing in base)"""
        await self.controller.update()
        self.assertTrue(True)  # Just verify it doesn't raise
        
    def test_cleanup(self):
        """Test cleanup handling"""
        self.controller.cleanup()
        self.assertTrue(self.controller.enabled)  # Should still be enabled after cleanup 