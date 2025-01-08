from .Device import Device

class RelayDevice(Device):
    """Interface for relay devices"""
    
    async def activate(self):
        """Activate the relay"""
        raise NotImplementedError
        
    async def deactivate(self):
        """Deactivate the relay"""
        raise NotImplementedError
        
    async def is_active(self):
        """Check if relay is active"""
        raise NotImplementedError 