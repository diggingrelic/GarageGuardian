from ..core.Events import EventSystem
from ..hardware.interfaces.Base import BaseDevice
from ..logging.Log import error
import time

class BaseController:
    """Base controller for all device controllers
    
    Provides common functionality for device monitoring,
    event publishing, and error handling.
    """
    
    def __init__(self, device: BaseDevice, event_system: EventSystem):
        self.device = device
        self.events = event_system
        self._last_check = 0.0
        self._check_interval = 1.0  # seconds
        
    async def publish_event(self, event_type: str, data: dict = None):
        """Publish an event with standard metadata
        
        Args:
            event_type (str): Type of event to publish
            data (dict, optional): Event specific data
        """
        if data is None:
            data = {}
            
        data.update({
            "timestamp": time.time(),
            "device_working": self.device.is_working()
        })
        
        await self.events.publish(event_type, data)
        
    async def publish_error(self, error_msg: str):
        """Publish a device error event
        
        Args:
            error_msg (str): Error message to publish
        """
        error(f"{self.__class__.__name__}: {error_msg}")
        await self.publish_event(f"{self.device_type}_error", {
            "error": error_msg
        })
        
    @property
    def device_type(self) -> str:
        """Get the type of device this controls"""
        return self.__class__.__name__.lower().replace('controller', '')
        
    def should_check(self) -> bool:
        """Check if enough time has passed for next device check"""
        now = time.time()
        if now - self._last_check >= self._check_interval:
            self._last_check = now
            return True
        return False