from micropython import const # type: ignore
from collections import deque
import time
import asyncio

# Event system constants
MAX_SUBSCRIBERS = const(20)  # Per event type
MAX_HISTORY = const(50)     # Maximum events to keep in history

class Event:
    def __init__(self, event_type, data=None):
        self.type = event_type
        self.data = data
        self.timestamp = time.time()
        self.handled = False

class EventSystem:
    def __init__(self):
        self.subscribers = {}      # Dictionary of event subscribers
        self.history = deque((), 10)
        self.stats = {
            'processed': 0,
            'dropped': 0,
            'errors': 0
        }

    def subscribe(self, event_type, handler):
        """Add an event handler"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        if len(self.subscribers[event_type]) < MAX_SUBSCRIBERS:
            if handler not in self.subscribers[event_type]:
                self.subscribers[event_type].append(handler)
                return True
        return False

    def unsubscribe(self, event_type, handler):
        """Remove an event handler"""
        if event_type in self.subscribers:
            if handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)
                return True
        return False

    async def publish(self, event_type, data=None):
        """Publish an event to all subscribers"""
        try:
            event = Event(event_type, data)
            self.history.append(event)
            
            if event_type in self.subscribers:
                tasks = []
                for handler in self.subscribers[event_type]:
                    try:
                        # Simpler async check and execution
                        if hasattr(handler, '__call__'):  # Check if callable
                            if hasattr(handler, 'is_coroutine') or hasattr(handler, '_is_coroutine'):
                                tasks.append(handler(event))
                            else:
                                handler(event)
                    except Exception as e:
                        print(f"Handler error: {e}")
                        
                if tasks:
                    for task in tasks:
                        await task
                    
                event.handled = True
                self.stats['processed'] += 1
            else:
                self.stats['dropped'] += 1
                
        except Exception as e:
            print(f"Event publish error: {e}")
            self.stats['errors'] += 1

    def get_recent_events(self, event_type=None, limit=10):
        """Get recent events, optionally filtered by type"""
        if event_type:
            events = [e for e in self.history if e.type == event_type]
        else:
            events = list(self.history)
        return events[-limit:]

    def get_stats(self):
        """Get event system statistics"""
        stats = {
            'processed': self.stats['processed'],
            'dropped': self.stats['dropped'],
            'errors': self.stats['errors'],
            'subscribers': {}
        }
        # Add subscriber counts
        for k, v in self.subscribers.items():
            stats['subscribers'][k] = len(v)
        return stats

    def clear_history(self):
        """Clear event history"""
        self.history.clear()
