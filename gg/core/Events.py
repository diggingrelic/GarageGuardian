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
        self.subscribers = {}  # event_type -> list of handlers
        self.stats = {
            "published": 0,
            "handled": 0,
            "errors": 0
        }
        
    async def start(self):
        """Initialize the event system"""
        self.subscribers = {}
        return True
        
    async def stop(self):
        """Clean shutdown of event system"""
        self.subscribers = {}
        return True
        
    def subscribe(self, event_type: str, handler) -> bool:
        """Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async function to handle event
        Returns:
            bool: True if subscription successful
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        if len(self.subscribers[event_type]) >= MAX_SUBSCRIBERS:
            return False
            
        self.subscribers[event_type].append(handler)
        return True
        
    async def publish(self, event_type: str, data=None):
        """Publish an event
        
        Args:
            event_type: Type of event to publish
            data: Optional data to pass to handlers
        """
        self.stats["published"] += 1
        
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    await handler({"type": event_type, "data": data})
                    self.stats["handled"] += 1
                except Exception:
                    self.stats["errors"] += 1
