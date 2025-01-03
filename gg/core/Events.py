from micropython import const # type: ignore
import asyncio # noqa: F401

# Event system constants
MAX_SUBSCRIBERS = const(20)

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
    """Event system for managing publish/subscribe patterns
    
    The EventSystem provides a way to decouple components through events.
    It supports both synchronous and asynchronous event handlers.
    
    Attributes:
        subscribers (dict): Dictionary mapping event names to lists of handlers
        stats (dict): Statistics about processed, dropped, and error events
    """
    def __init__(self):
        """Initialize a new event system"""
        self.subscribers = {}
        self.stats = {
            'processed': 0,
            'dropped': 0,
            'errors': 0
        }

    def subscribe(self, event_name, handler):
        """Subscribe a handler to an event
        
        Args:
            event_name (str): Name of the event to subscribe to
            handler (callable): Function to handle the event
            
        Returns:
            bool: True if subscription successful, False if at subscriber limit
            
        Example:
            >>> def on_temperature(event):
            ...     print(f"Temperature: {event.data}")
            >>> events.subscribe("temperature_change", on_temperature)
        """
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        if len(self.subscribers[event_name]) >= MAX_SUBSCRIBERS:
            return False
        self.subscribers[event_name].append(handler)
        return True

    async def publish(self, event_name, event_data=None):
        """Publish an event to all subscribers
        
        Args:
            event_name (str): Name of the event to publish
            event_data (any, optional): Data to include with the event
            
        Example:
            >>> await events.publish("temperature_change", {"temp": 25.5})
        """
        event = Event(event_name, event_data)
        if event_name in self.subscribers:
            for handler in self.subscribers[event_name]:
                try:
                    if hasattr(handler, '__await__'):
                        await handler(event)
                    else:
                        handler(event)
                    self.stats['processed'] += 1
                except Exception as e:
                    self.stats['errors'] += 1
                    raise e
        else:
            self.stats['dropped'] += 1
