from ..microtest import TestCase
from ...controllers.Base import BaseController
from ...core.Events import EventSystem
from ...core.Safety import SafetyMonitor
from ..mocks.MockDoor import MockDoor
import gc

class TestBaseController(TestCase):
    def __init__(self):
        """Initialize the test case"""
        super().__init__()
        self.controller = None
        self.hardware = None
        self.events = None
        self.safety = None
        
    def setUp(self):
        """Initialize test components"""
        self.hardware = MockDoor()
        self.events = EventSystem()
        self.safety = SafetyMonitor()
        self.controller = BaseController("test", self.hardware, self.safety, self.events)
        
    def tearDown(self):
        """Clean up after test"""
        if hasattr(self, 'controller') and self.controller:
            self.controller.cleanup()
        self.controller = None
        self.hardware = None
        self.events = None
        self.safety = None
        gc.collect()
        
    async def test_cleanup(self):
        """Test cleanup handling"""
        self.assertTrue(self.controller.enabled)
        self.controller.cleanup()
        self.assertFalse(self.controller.enabled)
        
    async def test_initialization(self):
        """Test basic initialization"""
        result = await self.controller.initialize()
        self.assertTrue(result)
        self.assertTrue(self.controller.enabled)
        self.assertEqual(self.controller.name, "test")
        
    async def test_attributes(self):
        """Test controller attributes"""
        self.assertEqual(self.controller.hardware, self.hardware)
        self.assertEqual(self.controller.safety, self.safety)
        self.assertEqual(self.controller.events, self.events)
        
    async def test_update(self):
        """Test update method (should do nothing in base)"""
        await self.controller.update()
        self.assertTrue(True)  # Just verify it doesn't raise 