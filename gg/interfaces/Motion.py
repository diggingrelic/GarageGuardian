from .Base import BaseDevice

class MotionDevice(BaseDevice):
    """Interface for motion sensor hardware"""
    
    def detect_motion(self) -> bool:
        """Check if motion is currently detected"""
        raise NotImplementedError
        
    def get_last_motion(self) -> float:
        """Get timestamp of last detected motion"""
        raise NotImplementedError
        
    def get_sensitivity(self) -> int:
        """Get current sensitivity level (1-10)"""
        raise NotImplementedError
        
    def set_sensitivity(self, level: int) -> bool:
        """Set motion detection sensitivity
        
        Args:
            level: Sensitivity level (1-10)
            
        Returns:
            bool: True if successfully set
        """
        raise NotImplementedError 