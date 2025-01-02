from .microtest import TestCase
from ..IoTController import IoTController
from .mocks import MockPin
import gc

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
        # Create a new controller instance for this test
        test_controller = IoTController()
        
        # Test error logging
        error_msg = "Test error"
        test_controller._log_error(error_msg)
        
        # Check error log
        self.assertTrue(len(test_controller.error_log) > 0)
        self.assertEqual(test_controller.error_log[0]["message"], error_msg)
        
        # Test error state transition
        test_controller.state = "error"
        self.assertEqual(test_controller.state, "error")
        
        # Explicit cleanup
        test_controller.events = None  # Break circular references
        test_controller = None  # Remove reference
        gc.collect()  # Force garbage collection 

    async def test_state_transitions(self):
        """Test state machine transitions"""
        # Test initial state
        self.assertEqual(self.controller.state, "initializing")
        
        # Test transition to ready
        await self.controller.initialize()
        self.assertEqual(self.controller.state, "ready")
        
        # Test transition to running
        self.controller.state = "running"
        self.assertEqual(self.controller.state, "running")
        
        # Test invalid state transition
        try:
            self.controller.state = "invalid_state"
            self.fail("Should not allow invalid state")
        except ValueError:
            pass

    async def test_event_subscription(self):
        """Test controller event subscriptions"""
        # Check that controller subscribes to required events
        self.assertIn("system_command", self.controller.events.subscribers)
        self.assertIn("system_state", self.controller.events.subscribers)
        self.assertIn("system_error", self.controller.events.subscribers)

    async def test_command_handling(self):
        """Test command processing"""
        # Initialize controller
        await self.controller.initialize()
        
        # Test stop command
        await self.controller.events.publish("system_command", {"command": "stop"})
        self.assertEqual(self.controller.state, "ready") 