from abc import abstractmethod
from .Base import BaseDevice

class DoorDevice(BaseDevice):
    """Interface for door hardware control"""
    
    @abstractmethod
    def is_open(self) -> bool:
        """Check if door is currently open"""
        pass
        
    @abstractmethod
    def is_locked(self) -> bool:
        """Check if door is currently locked"""
        pass
        
    @abstractmethod
    def lock(self) -> bool:
        """Lock the door"""
        pass
        
    @abstractmethod
    def unlock(self) -> bool:
        """Unlock the door"""
        pass 