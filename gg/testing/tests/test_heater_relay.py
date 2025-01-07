from ..microtest import TestCase
from ...devices.HeaterRelay import HeaterRelay
import gc
import time

class TestHeaterRelay(TestCase):
    def __init__(self):
        """Initialize the test case"""
        super().__init__()
        self.heater = None
        
    def setUp(self):
        """Initialize test components"""
        self.heater = HeaterRelay()
        
    def tearDown(self):
        """Clean up after test"""
        if self.heater:
            self.heater._pin.off()  # Direct pin control for cleanup
            time.sleep(1)  # Safety delay
        self.heater = None
        gc.collect()
        
    async def test_initialization(self):
        """Test heater relay initialization"""
        self.assertFalse(await self.heater.is_active())
        
    async def test_activation(self):
        """Test heater relay activation"""
        await self.heater.activate()
        time.sleep(1)  # Allow relay to settle
        self.assertTrue(await self.heater.is_active())
        
    async def test_deactivation(self):
        """Test heater relay deactivation"""
        # First activate
        await self.heater.activate()
        time.sleep(1)  # Allow relay to settle
        self.assertTrue(await self.heater.is_active())
        
        # Then deactivate
        await self.heater.deactivate()
        time.sleep(1)  # Allow relay to settle
        self.assertFalse(await self.heater.is_active())
        
    async def test_rapid_switching(self):
        """Test protection against rapid switching"""
        await self.heater.activate()
        time.sleep(1)
        await self.heater.deactivate()
        
        # Try to activate before cycle delay
        with self.assertRaises(ValueError):
            await self.heater.activate() 