from abc import ABC, abstractmethod
import time

class BaseDevice(ABC):
    """Base interface for all hardware devices
    
    Provides common functionality and required methods
    for all device implementations.
    """
    
    def __init__(self):
        self._last_reading = 0.0
        self._error_count = 0
        self._max_errors = 3
        
    @abstractmethod
    def is_working(self) -> bool:
        """Check if device is functioning properly
        
        Returns:
            bool: True if device is working, False if failed
        """
        pass
        
    def last_reading_time(self) -> float:
        """Get timestamp of last successful reading
        
        Returns:
            float: Unix timestamp of last reading
        """
        return self._last_reading
        
    def record_reading(self):
        """Update last reading timestamp"""
        self._last_reading = time.time()
        
    def record_error(self) -> bool:
        """Record an error and check if device exceeded max errors
        
        Returns:
            bool: True if device should be considered failed
        """
        self._error_count += 1
        return self._error_count >= self._max_errors 