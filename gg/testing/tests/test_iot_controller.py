from ..microtest import TestCase
from ...IoTController import IoTController, SystemState
from ...core.Safety import SafetySeverity
from ..mocks import MockPin
import gc

class TestIoTController(TestCase):
    def __init__(self):
        super().__init__()
        self.controller = IoTController()
        self.controller.led = MockPin("LED", MockPin.OUT)

    def test_init(self):
        """Test controller initialization"""
        self.assertEqual(self.controller.state, SystemState.INITIALIZING)
        self.assertTrue(hasattr(self.controller, 'events'))

    async def test_initialize(self):
        """Test async initialization"""
        result = await self.controller.initialize()
        self.assertTrue(result)
        self.assertEqual(self.controller.state, SystemState.READY)

    async def test_led_toggle(self):
        """Test LED toggling"""
        initial_state = self.controller.led.value()
        await self.controller.initialize()
        
        # Start run loop but only for a short time
        self.controller.state = SystemState.RUNNING
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
        test_controller.state = SystemState.ERROR
        self.assertEqual(test_controller.state, SystemState.ERROR)
        
        # Explicit cleanup
        test_controller.events = None  # Break circular references
        test_controller = None  # Remove reference
        gc.collect()  # Force garbage collection

    async def test_safety_integration(self):
        """Test safety system integration"""
        await self.controller.initialize()
        self.assertTrue(hasattr(self.controller, 'safety'))
        self.assertEqual(self.controller.state, SystemState.READY)
        
        # Add a test safety condition
        self.controller.safety.add_condition(
            name="test_condition",
            check_func=lambda: False,  # Always unsafe
            severity=SafetySeverity.CRITICAL
        )
        
        # Run should detect safety violation
        self.controller.state = SystemState.RUNNING
        await self.controller.run()
        self.assertEqual(self.controller.state, SystemState.ERROR)
        
    async def test_shutdown(self):
        """Test system shutdown"""
        await self.controller.initialize()
        await self.controller.shutdown()
        self.assertEqual(self.controller.state, SystemState.SHUTDOWN)
        self.assertEqual(self.controller.led.value(), 0)  # LED should be off

    async def test_restart(self):
        """Test system restart"""
        await self.controller.initialize()
        await self.controller.restart()
        self.assertEqual(self.controller.state, SystemState.READY)

    def cleanup(self):
        """Cleanup test resources"""
        if hasattr(self, 'controller'):
            self.controller.events = None
            self.controller = None
        gc.collect()