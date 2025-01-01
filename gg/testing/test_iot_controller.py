from .microtest import TestCase
from ..IoTController import IoTController
from .mocks import MockPin

class TestIoTController(TestCase):
    def __init__(self):
        super().__init__()
        self.controller = IoTController()
        self.controller.led = MockPin("LED", MockPin.OUT)

    def test_init(self):
        """Test controller initialization"""
        self.assertEqual(self.controller.state, "initializing")
        self.assertTrue(hasattr(self.controller, 'events'))

    async def test_initialize(self):
        """Test async initialization"""
        result = await self.controller.initialize()
        self.assertTrue(result)
        self.assertEqual(self.controller.state, "ready")

    async def test_led_toggle(self):
        """Test LED toggling"""
        initial_state = self.controller.led.value()
        await self.controller.initialize()
        
        # Start run loop but only for a short time
        self.controller.state = "running"
        await self.controller.run()
        
        # Check that LED state changed
        self.assertNotEqual(initial_state, self.controller.led.value()) 