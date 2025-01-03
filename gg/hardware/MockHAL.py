from .Interfaces import PinInterface, DoorInterface
import asyncio

class MockPin(PinInterface):
    """Mock implementation for testing"""
    def __init__(self, pin_id, mode):
        super().__init__(pin_id)
        self._value = 0
        self.mode = mode
        
    def set_high(self):
        self._value = 1
        
    def set_low(self):
        self._value = 0
        
    def read(self):
        return self._value

class MockDoor(DoorInterface):
    """Mock implementation for testing door hardware"""
    def __init__(self):
        super().__init__()
        self._position = 0  # 0=closed, 1=open
        self._moving = False
        self._obstructed = False
        
    async def open(self):
        self._moving = True
        self._position = 1
        await asyncio.sleep_ms(100)  # Simulate movement time
        self._moving = False
        
    async def close(self):
        self._moving = True
        self._position = 0
        await asyncio.sleep_ms(100)  # Simulate movement time
        self._moving = False
        
    async def stop(self):
        self._moving = False
        
    def is_fully_open(self):
        return self._position == 1
        
    def is_fully_closed(self):
        return self._position == 0
        
    def is_obstructed(self):
        return self._obstructed
        
    # Test helper methods
    def simulate_obstruction(self, is_obstructed):
        self._obstructed = is_obstructed 