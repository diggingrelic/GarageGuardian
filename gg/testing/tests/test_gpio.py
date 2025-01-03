from ..microtest import TestCase
from ...hardware.GPIO import GPIOManager
from ...hardware.MockHAL import MockPin

class TestGPIO(TestCase):
    def __init__(self):
        super().__init__()
        # Initialize GPIO with mock hardware
        self.gpio = GPIOManager(hardware_interface=MockPin)
        
    def test_pin_setup(self):
        """Test GPIO setup"""
        result = self.gpio.setup("led", 1, GPIOManager.OUT)
        self.assertTrue(result)
        self.assertTrue("led" in self.gpio.pins)
        
    def test_pin_write(self):
        """Test GPIO write"""
        self.gpio.setup("led", 1, GPIOManager.OUT)
        # Write high
        self.assertTrue(self.gpio.write("led", True))
        self.assertEqual(self.gpio.read("led"), 1)
        # Write low
        self.assertTrue(self.gpio.write("led", False))
        self.assertEqual(self.gpio.read("led"), 0)
        
    def test_pin_read(self):
        """Test GPIO read"""
        self.gpio.setup("button", 2, GPIOManager.IN)
        # Initial state should be low
        self.assertEqual(self.gpio.read("button"), 0)
        # Set high and read
        self.gpio.pins["button"].set_high()
        self.assertEqual(self.gpio.read("button"), 1)
        
    def test_invalid_operations(self):
        """Test invalid pin operations"""
        # Read non-existent pin
        self.assertEqual(self.gpio.read("invalid"), -1)
        # Write to non-existent pin
        self.assertFalse(self.gpio.write("invalid", True))
        
    def test_cleanup(self):
        """Test GPIO cleanup"""
        self.gpio.setup("test", 1, GPIOManager.OUT)
        self.gpio.write("test", True)
        self.gpio.cleanup()
        self.assertEqual(len(self.gpio.pins), 0) 