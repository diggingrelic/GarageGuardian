from ..hardware.interfaces.Motion import MotionDevice
from .Base import BaseController

class MotionController(BaseController):
    """Controller for motion sensor operations
    
    Manages a motion sensor and integrates it with the event system.
    Monitors motion detection and publishes relevant events.
    
    Events published:
        - motion_detected: When motion is first detected
        - motion_cleared: When motion is no longer detected
        - motion_error: When sensor operation fails
    """
    
    def __init__(self, sensor: MotionDevice, event_system):
        super().__init__(sensor, event_system)
        self._last_motion_state = False
        self._sensitivity = 5  # Default sensitivity
        
    async def monitor(self):
        """Monitor motion detection state"""
        if not self.should_check():
            return
            
        try:
            motion_detected = self.device.detect_motion()
            
            # Publish events on state changes
            if motion_detected != self._last_motion_state:
                event = "motion_detected" if motion_detected else "motion_cleared"
                await self.publish_event(event, {
                    "last_motion": self.device.get_last_motion(),
                    "sensitivity": self.device.get_sensitivity()
                })
                self._last_motion_state = motion_detected
                
        except Exception as e:
            await self.publish_error(f"Detection failed: {e}")
            
    async def set_sensitivity(self, level: int) -> bool:
        """Adjust motion detection sensitivity
        
        Args:
            level (int): Sensitivity level (1-10)
            
        Returns:
            bool: True if sensitivity was set successfully
        """
        try:
            if self.device.set_sensitivity(level):
                await self.publish_event("motion_sensitivity_changed", {
                    "level": level
                })
                return True
            return False
        except Exception as e:
            await self.publish_error(f"Sensitivity adjustment failed: {e}")
            return False 