import time

class BaseDevice:
    """Base interface for all hardware devices"""
    def __init__(self):
        self._last_reading = 0.0
        self._error_count = 0
        self._max_errors = 3
        
    async def is_working(self):
        """Check if device is functioning properly"""
        return self._error_count < self._max_errors
        
    async def last_reading_time(self):
        """Get timestamp of last reading"""
        return self._last_reading
        
    async def record_reading(self):
        """Record a successful reading"""
        self._last_reading = time.time()
        
    async def record_error(self):
        """Record an error occurrence
        
        Returns:
            bool: True if error count exceeds max_errors
        """
        self._error_count += 1
        return self._error_count >= self._max_errors 