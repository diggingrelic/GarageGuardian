from ..microtest import TestCase
from ...interfaces.Base import BaseDevice
from ...interfaces.Door import DoorDevice
from ...interfaces.Temperature import TemperatureDevice
from ...interfaces.Motion import MotionDevice
import gc

class TestBaseInterface(TestCase):
    def __init__(self):
        """Initialize the test case"""
        super().__init__()
        self.device = None
        
    def setUp(self):
        """Initialize test components"""
        self.device = BaseDevice()
        
    def tearDown(self):
        """Clean up after test"""
        self.device = None
        gc.collect()
        
    async def test_error_tracking(self):
        """Test error counting functionality"""
        self.assertTrue(self.device.is_working())
        
        # Record errors up to limit
        for _ in range(self.device._max_errors - 1):
            self.assertFalse(self.device.record_error())
            self.assertTrue(self.device.is_working())
            
        # One more error should mark device as not working
        self.assertTrue(self.device.record_error())
        self.assertFalse(self.device.is_working())
        
    async def test_reading_timestamp(self):
        """Test reading timestamp tracking"""
        initial_time = self.device.last_reading_time()
        self.device.record_reading()
        self.assertTrue(self.device.last_reading_time() > initial_time)

class TestDoorInterface(TestCase):
    def test_required_methods(self):
        """Verify required methods"""
        required_methods = [
            'is_open',
            'is_locked',
            'lock',
            'unlock',
            'is_working'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(DoorDevice, method))
            
class TestTemperatureInterface(TestCase):
    def test_required_methods(self):
        """Verify required methods"""
        required_methods = [
            'get_fahrenheit',
            'get_celsius',
            'is_working'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(TemperatureDevice, method))
            
class TestMotionInterface(TestCase):
    def test_required_methods(self):
        """Verify required methods"""
        required_methods = [
            'detect_motion',
            'get_last_motion',
            'get_sensitivity',
            'set_sensitivity',
            'is_working'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(MotionDevice, method)) 