from ...hardware.interfaces.Motion import MotionDevice
import time

class MockMotion(MotionDevice):
    """Mock implementation of a motion sensor for testing
    
    Simulates a motion sensor with configurable sensitivity
    and detection state.
    """
    
    def __init__(self, initial_sensitivity: int = 5):
        super().__init__()
        self._motion_detected = False
        self._sensitivity = initial_sensitivity
        self._last_motion = 0.0
        self.record_reading()
        
    def detect_motion(self) -> bool:
        """Check if mock motion is detected"""
        self.record_reading()
        return self._motion_detected
        
    def get_last_motion(self) -> float:
        """Get timestamp of last mock motion"""
        return self._last_motion
        
    def get_sensitivity(self) -> int:
        """Get current mock sensitivity level"""
        return self._sensitivity
        
    def set_sensitivity(self, level: int) -> bool:
        """Set mock sensitivity level"""
        if not 1 <= level <= 10:
            self.record_error()
            return False
        self._sensitivity = level
        return True
        
    def is_working(self) -> bool:
        """Check if mock sensor is functioning"""
        return self._error_count < self._max_errors
        
    # Test helper methods
    def simulate_motion(self):
        """Simulate motion detection"""
        self._motion_detected = True
        self._last_motion = time.time()
        self.record_reading()
        
    def simulate_clear(self):
        """Simulate no motion"""
        self._motion_detected = False
        self.record_reading() 