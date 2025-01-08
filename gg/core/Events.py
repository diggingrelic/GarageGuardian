from micropython import const # type: ignore
import asyncio # noqa: F401

# Event system constants
MAX_SUBSCRIBERS = 10  # Maximum subscribers per event type

class Event:
    """Event object for type safety and future extensibility
    
    Attributes:
        name (str): Name of the event
        data (any): Optional data associated with the event
    """
    def __init__(self, name, data=None):
        """Initialize a new event
        
        Args:
            name (str): Name of the event
            data (any, optional): Data associated with the event. Defaults to None.
        """
        self.name = name
        self.data = data
        
    def __str__(self):
        """String representation of the event
        
        Returns:
            str: Event name
        """
        return self.name

class EventSystem:
    """Simple event system for MicroPython"""
    
    def __init__(self):
        self.subscribers = {}
        
    async def start(self):
        """Initialize event system"""
        return True
        
    async def stop(self):
        """Stop event system"""
        self.subscribers.clear()
        return True
        
    def subscribe(self, event_type, handler):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    async def publish(self, event_type, data=None):
        """Publish an event"""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                await handler(data)
