class Device:
    """Base interface for all hardware devices"""
    
    async def initialize(self):
        """Initialize the device"""
        return True
        
    async def is_working(self):
        """Check if device is functioning"""
        return True 