from ...hardware.interfaces.Door import DoorDevice
import time

class MockDoor(DoorDevice):
    """Mock implementation of a door device for testing
    
    Simulates a door with a sensor and lock mechanism.
    """
    
    def __init__(self):
        super().__init__()
        self._is_open = False
        self._is_locked = False
        self.record_reading()
        
    def is_open(self) -> bool:
        """Check if mock door is open"""
        self.record_reading()
        return self._is_open
        
    def is_locked(self) -> bool:
        """Check if mock door is locked"""
        self.record_reading()
        return self._is_locked
        
    def lock(self) -> bool:
        """Lock the mock door"""
        if self._is_open:
            self.record_error()
            return False
        self._is_locked = True
        self.record_reading()
        return True
        
    def unlock(self) -> bool:
        """Unlock the mock door"""
        self._is_locked = False
        self.record_reading()
        return True
        
    def is_working(self) -> bool:
        """Check if mock door is functioning"""
        return self._error_count < self._max_errors
        
    # Test helper methods
    def simulate_open(self):
        """Simulate door being opened"""
        self._is_open = True
        self.record_reading()
        
    def simulate_close(self):
        """Simulate door being closed"""
        self._is_open = False
        self.record_reading() 