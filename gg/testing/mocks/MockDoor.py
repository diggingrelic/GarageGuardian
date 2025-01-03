from ...interfaces.Door import DoorDevice

class MockDoor(DoorDevice):
    """Mock implementation of a door device for testing
    
    Simulates a door with a sensor and lock mechanism.
    """
    
    def __init__(self):
        super().__init__()
        self._is_open = False
        self._is_locked = False
        self._last_reading = 0.0  # Direct assignment instead of await
        
    async def is_open(self):
        """Check if mock door is open"""
        await self.record_reading()
        return self._is_open
        
    async def is_locked(self):
        """Check if mock door is locked"""
        await self.record_reading()
        return self._is_locked
        
    async def lock(self):
        """Lock the mock door"""
        if self._is_open:
            await self.record_error()
            return False
        self._is_locked = True
        await self.record_reading()
        return True
        
    async def unlock(self):
        """Unlock the mock door"""
        self._is_locked = False
        await self.record_reading()
        return True
        
    async def is_working(self):
        """Check if mock door is functioning"""
        return await super().is_working()
        
    # Test helper methods
    async def simulate_open(self):
        """Simulate door being opened"""
        self._is_open = True
        await self.record_reading()
        
    async def simulate_close(self):
        """Simulate door being closed"""
        self._is_open = False
        await self.record_reading() 