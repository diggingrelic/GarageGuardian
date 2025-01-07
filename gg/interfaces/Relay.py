from .Base import BaseDevice

class RelayDevice(BaseDevice):
    """Interface for relay hardware control"""
    
    async def activate(self):
        """Activate/turn on the relay"""
        raise NotImplementedError
        
    async def deactivate(self):
        """Deactivate/turn off the relay"""
        raise NotImplementedError
        
    async def is_active(self):
        """Check if relay is currently activated"""
        raise NotImplementedError 