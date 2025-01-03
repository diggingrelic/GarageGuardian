from .Base import BaseDevice

class DoorDevice(BaseDevice):
    """Interface for door hardware control"""
    
    def is_open(self) -> bool:
        """Check if door is currently open"""
        raise NotImplementedError
        
    def is_locked(self) -> bool:
        """Check if door is currently locked"""
        raise NotImplementedError
        
    def lock(self) -> bool:
        """Lock the door
        
        Returns:
            bool: True if successfully locked
        """
        raise NotImplementedError
        
    def unlock(self) -> bool:
        """Unlock the door
        
        Returns:
            bool: True if successfully unlocked
        """
        raise NotImplementedError 