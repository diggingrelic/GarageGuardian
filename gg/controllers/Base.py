from ..core.Events import EventSystem
from ..interfaces.Base import BaseDevice
from ..logging.Log import error
import time

class BaseController:
    """Base controller for all device controllers"""
    
    def __init__(self, name: str, hardware, safety, events):
        """Initialize controller
        
        Args:
            name: Controller name/identifier
            hardware: Hardware device interface
            safety: Safety monitor instance
            events: Event system instance
        """
        self.name = name
        self.hardware = hardware
        self.safety = safety
        self.events = events
        self.enabled = True
        
    async def initialize(self):
        """Initialize the controller
        
        Returns:
            bool: True if initialization successful
        """
        await self.events.start()  # Ensure events system is started
        await self.safety.start()  # Ensure safety system is started
        return True
        
    async def update(self):
        """Update controller state"""
        pass
        
    def cleanup(self):
        """Clean up controller resources"""
        self.enabled = False