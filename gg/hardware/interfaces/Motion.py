from abc import abstractmethod
from typing import Tuple
from .Base import BaseDevice

class MotionDevice(BaseDevice):
    """Interface for motion sensor hardware
    
    Defines the required methods any motion sensor implementation
    (real or mock) must provide.
    """
    
    @abstractmethod
    def detect_motion(self) -> bool:
        """Check if motion is currently detected
        
        Returns:
            bool: True if motion detected, False otherwise
        """
        pass
        
    @abstractmethod
    def get_last_motion(self) -> float:
        """Get timestamp of last detected motion
        
        Returns:
            float: Unix timestamp of last motion detection
        """
        pass
        
    @abstractmethod
    def get_sensitivity(self) -> int:
        """Get current sensitivity level
        
        Returns:
            int: Sensitivity level (typically 1-10)
        """
        pass
        
    @abstractmethod
    def set_sensitivity(self, level: int) -> bool:
        """Set motion detection sensitivity
        
        Args:
            level (int): Sensitivity level (typically 1-10)
            
        Returns:
            bool: True if sensitivity was set successfully
        """
        pass 