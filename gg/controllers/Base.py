from ..logging.Log import error
import time

class BaseController:
    """Base controller for all device controllers"""
    
    def __init__(self, name: str, hardware, safety, events):
        self.name = name
        self.hardware = hardware
        self.safety = safety
        self.events = events
        self.enabled = True
        
    async def initialize(self):
        """Initialize the controller"""
        return await self.hardware.initialize()
        
    async def monitor(self):
        """Monitor device state - must be implemented by subclasses"""
        raise NotImplementedError
        
    async def cleanup(self):
        """Clean up controller resources"""
        self.enabled = False
        await self.events.publish("controller_disabled", {
            "name": self.name,
            "timestamp": time.time()
        })
        
    async def publish_event(self, event_type, data=None):
        """Publish an event with optional data"""
        if data is None:
            data = {}
        data["controller"] = self.name
        await self.events.publish(event_type, data)
        
    async def publish_error(self, message: str):
        """Publish an error event"""
        error(f"{self.name}: {message}")
        await self.publish_event("controller_error", {
            "error": message,
            "timestamp": time.time()
        })