from micropython import const
import asyncio
from ..logging.Log import error

# Event system constants
MAX_SUBSCRIBERS = const(20)

class Event:
    """Event object for type safety and future extensibility"""
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        
    def __str__(self):
        return self.name

class EventSystem:
    def __init__(self):
        self.subscribers = {}
        self.stats = {
            'processed': 0,
            'dropped': 0,
            'errors': 0
        }

    def subscribe(self, event_name, handler):
        """Subscribe a handler to an event"""
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        if len(self.subscribers[event_name]) >= MAX_SUBSCRIBERS:
            return False
        self.subscribers[event_name].append(handler)
        return True

    async def publish(self, event_name, event_data=None):
        """Publish an event to all subscribers"""
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
