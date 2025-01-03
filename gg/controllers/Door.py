from ..hardware.interfaces.Door import DoorDevice
from .Base import BaseController

class DoorController(BaseController):
    """Controller for door operations and monitoring
    
    Manages a door device and integrates it with the event system.
    Handles door state changes and publishes relevant events.
    
    Events published:
        - door_opened: When door changes from closed to open
        - door_closed: When door changes from open to closed
        - door_locked: When door is successfully locked
        - door_unlocked: When door is successfully unlocked
        - door_error: When door operation fails
    """
    
    def __init__(self, door: DoorDevice, event_system):
        super().__init__(door, event_system)
        self._last_state = None
        
    async def monitor(self):
        """Monitor door state and publish changes"""
        if not self.should_check():
            return
            
        try:
            is_open = self.device.is_open()
            
            if self._last_state != is_open:
                event = "door_opened" if is_open else "door_closed"
                await self.publish_event(event)
                self._last_state = is_open
                
        except Exception as e:
            await self.publish_error(f"Monitoring failed: {e}")
            
    async def lock(self) -> bool:
        """Lock the door
        
        Returns:
            bool: True if door was locked successfully
        """
        try:
            if self.device.lock():
                await self.publish_event("door_locked")
                return True
            return False
        except Exception as e:
            await self.publish_error(f"Lock failed: {e}")
            return False
            
    async def unlock(self) -> bool:
        """Unlock the door
        
        Returns:
            bool: True if door was unlocked successfully
        """
        try:
            if self.device.unlock():
                await self.publish_event("door_unlocked")
                return True
            return False
        except Exception as e:
            await self.publish_error(f"Unlock failed: {e}")
            return False 