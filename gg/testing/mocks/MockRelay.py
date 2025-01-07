from ...interfaces.Relay import RelayDevice

class MockRelay(RelayDevice):
    """Mock implementation of a relay device for testing"""
    
    def __init__(self):
        super().__init__()
        self._active = False
        self._last_reading = 0.0
        
    async def activate(self):
        """Activate mock relay"""
        self._active = True
        await self.record_reading()
        
    async def deactivate(self):
        """Deactivate mock relay"""
        self._active = False
        await self.record_reading()
        
    async def is_active(self):
        """Check if mock relay is activated"""
        await self.record_reading()
        return self._active
        
    # Test helper methods
    async def simulate_failure(self):
        """Simulate a relay failure"""
        await self.record_error() 