import unittest
import asyncio
from gg.IoTController import IoTController
from .mocks import MockPin

class TestIoTController(unittest.TestCase):
    def setUp(self):
        # Use our mock pin instead of real hardware
        self.controller = IoTController()
        self.controller.led = MockPin("LED", MockPin.OUT)

    def test_init(self):
        """Test controller initialization"""
        self.assertEqual(self.controller.state, "initializing")
        self.assertIsNotNone(self.controller.events)

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
        run_task = asyncio.create_task(self.controller.run())
        await asyncio.sleep(2)  # Let it run for 2 seconds
        
        # Check that LED state changed
        self.assertNotEqual(initial_state, self.controller.led.value())
        
        # Cleanup
        self.controller.state = "shutdown"
        await run_task 