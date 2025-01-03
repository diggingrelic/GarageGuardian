from ...interfaces.Motion import MotionDevice

class MockMotion(MotionDevice):
    """Mock implementation of a motion sensor for testing
    
    Simulates a motion sensor with configurable sensitivity.
    """
    
    def __init__(self):
        super().__init__()
        self._motion_detected = False
        self._sensitivity = 5  # Mid-range default
        self._last_reading = 0.0  # Direct assignment instead of await
        
    async def detect_motion(self):
        """Check if motion is currently detected"""
        await self.record_reading()
        return self._motion_detected
        
    async def get_last_motion(self):
        """Get timestamp of last motion detection"""
        return await self.last_reading_time()
        
    async def get_sensitivity(self):
        """Get current sensitivity setting"""
        await self.record_reading()
        return self._sensitivity
        
    async def set_sensitivity(self, level):
        """Set motion detection sensitivity
        
        Args:
            level: Sensitivity level (1-10)
        Returns:
            bool: True if setting was valid and applied
        """
        if 1 <= level <= 10:
            self._sensitivity = level
            await self.record_reading()
            return True
        return False
        
    async def is_working(self):
        """Check if mock sensor is functioning"""
        return await super().is_working()
        
    # Test helper methods
    async def simulate_motion(self):
        """Simulate motion detection"""
        self._motion_detected = True
        await self.record_reading()
        
    async def simulate_clear(self):
        """Simulate no motion"""
        self._motion_detected = False
        await self.record_reading()
        
    async def simulate_error(self):
        """Simulate a sensor error"""
        await self.record_error() 