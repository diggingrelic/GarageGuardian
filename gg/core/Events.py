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
        self.subscribers = {}
        self.history = deque((), MAX_HISTORY)
        self.stats = {
            'processed': 0,
            'dropped': 0,
            'errors': 0,
            'subscribers': 0
        }

    def subscribe(self, event_type, handler):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            
        # Check subscriber limit
        current_count = len(self.subscribers[event_type])
        if current_count > MAX_SUBSCRIBERS:
            return False
            
        self.subscribers[event_type].append(handler)
        self.stats['subscribers'] += 1
        return True

    async def publish(self, event_type, data=None):
        """Publish an event to all subscribers"""
        try:
            event = Event(event_type, data)
            self.history.append(event)
            
            if event_type in self.subscribers:
                tasks = []
                for handler in self.subscribers[event_type]:
                    try:
                        result = handler(event)
                        if hasattr(result, 'send'):
                            tasks.append(result)
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

    def get_stats(self):
        """Get event system statistics"""
        stats = self.stats.copy()
        stats.update({
            'event_types': len(self.subscribers),
            'history_size': len(self.history),
            'history_max': MAX_HISTORY
        })
        return stats

    def get_recent_events(self, count=None):
        """Get recent events from history"""
        if count is None:
            return list(self.history)
        return list(self.history)[-count:]
