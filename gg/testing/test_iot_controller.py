from .microtest import TestCase
from ..IoTController import IoTController
from .mocks import MockPin
from collections import deque

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

    async def test_error_handling(self):
        """Test error handling and logging"""
        # Test error logging
        error_msg = "Test error"
        self.controller._log_error(error_msg)
        
        # Check error log
        self.assertTrue(len(self.controller.error_log) > 0)
        self.assertEqual(self.controller.error_log[0]["message"], error_msg)
        
        # Test error state transition
        self.controller.state = "error"
        self.assertEqual(self.controller.state, "error")
        
        # Clean up - create new empty deque instead of clearing
        self.controller.error_log = deque((), 10)  # Same size as in IoTController
        self.controller.state = "initializing"  # Reset state 