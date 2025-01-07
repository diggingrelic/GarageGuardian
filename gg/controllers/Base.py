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
        """Initialize the controller"""
        await self.events.start()
        await self.safety.start()
        return True
        
    async def monitor(self):
        """Monitor device state - must be implemented by subclasses"""
        pass
        
    async def cleanup(self):
        """Clean up controller resources"""
        self.enabled = False
        await self.events.publish("controller_disabled", {
            "name": self.name,
            "timestamp": time.time()
        })
        
    async def publish_error(self, message: str):
        """Publish an error event"""
        error(f"{self.name}: {message}")
        await self.events.publish("controller_error", {
            "controller": self.name,
            "error": message,
            "timestamp": time.time()
        })
        
    async def publish_event(self, event_type: str, data: dict):
        """Publish an event through the event system"""
        event_data = data.copy()
        event_data["controller"] = self.name
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
        await self.events.publish(event_type, event_data)