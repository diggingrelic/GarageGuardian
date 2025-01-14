from ..microtest import TestCase
from ...system_controller import SystemController, SystemState
from ...core.Events import EventSystem
from ...controllers.Base import BaseController
from ...interfaces.Base import BaseDevice
from ...core.DeviceFactory import DeviceFactory
from ...core.Safety import SafetyMonitor
import gc

class MockDevice(BaseDevice):
    """Simple mock device for testing"""
    def __init__(self, working=True):
        super().__init__()
        self._working = working
        
    def is_working(self):
        return self._working

class MockController(BaseController):
    """Simple mock controller for testing"""
    def __init__(self, name, hardware, safety, events):
        super().__init__(name, hardware, safety, events)
        self.monitored = False
        
    async def update(self):
        self.monitored = True

class TestSystemController(TestCase):
    def setUp(self):
        self.events = EventSystem()
        self.safety = SafetyMonitor()
        self.device_factory = DeviceFactory()
        self.controller = SystemController(
            event_system=self.events,
            safety_monitor=self.safety
        )
        
    def tearDown(self):
        self.controller = None
        self.device_factory = None
        gc.collect()
        
    async def test_initialization(self):
        """Test system initialization"""
        self.assertEqual(self.controller.state, SystemState.INITIALIZING)
        result = await self.controller.initialize(device_factory=self.device_factory)
        self.assertTrue(result)
        self.assertEqual(self.controller.state, SystemState.RUNNING)
        
    async def test_device_registration(self):
        """Test device registration"""
        await self.controller.initialize_system()
        
        # Create mock device and controller
        device = MockDevice()
        mock = MockController("test", device, self.controller.safety, self.controller.events)
        
        # Register device
        self.assertTrue(self.controller.register_device("test", mock))
        self.assertEqual(len(self.controller.devices), 1)
        
        # Try duplicate registration
        self.assertFalse(self.controller.register_device("test", mock))
        
    async def test_monitoring(self):
        """Test device monitoring"""
        await self.controller.initialize_system()
        
        # Add device to monitor
        device = MockDevice()
        mock = MockController("test", device, self.controller.safety, self.controller.events)
        self.controller.register_device("test", mock)
        
        # Run monitoring cycle
        await self.controller.run()
        self.assertTrue(mock.monitored)
        
    async def test_shutdown(self):
        """Test system shutdown"""
        await self.controller.initialize_system()
        await self.controller.safe_shutdown()
        self.assertEqual(self.controller.state, SystemState.SHUTDOWN) 