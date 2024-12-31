import asyncio
from collections import defaultdict, deque
import time

class Event:
    def __init__(self, event_type, data=None, timestamp=None):
        self.type = event_type
        self.data = data
        self.timestamp = timestamp or time.time()
        self.handled = False

class EventSystem:
    def __init__(self):
        # Separate sync and async handlers
        self.sync_subscribers = defaultdict(list)
        self.async_subscribers = defaultdict(list)
        
        # Event history with limited size
        self.history = deque(maxlen=1000)
        
        # Event statistics
        self.stats = {
            'events_processed': 0,
            'events_dropped': 0,
            'handler_errors': 0
        }
        
        # Priority handlers get called first
        self.priority_handlers = defaultdict(list)
        
    def subscribe(self, event_type, handler, priority=False, is_async=False):
        """Subscribe to an event type"""
        if is_async:
            if handler not in self.async_subscribers[event_type]:
                self.async_subscribers[event_type].append(handler)
        else:
            if handler not in self.sync_subscribers[event_type]:
                self.sync_subscribers[event_type].append(handler)
                
        if priority:
            self.priority_handlers[event_type].append(handler)
            
    def unsubscribe(self, event_type, handler):
        """Remove a handler subscription"""
        self.sync_subscribers[event_type] = [
            h for h in self.sync_subscribers[event_type] if h != handler
        ]
        self.async_subscribers[event_type] = [
            h for h in self.async_subscribers[event_type] if h != handler
        ]
        self.priority_handlers[event_type] = [
            h for h in self.priority_handlers[event_type] if h != handler
        ]
            
    async def publish(self, event_type, data=None):
        """Publish an event"""
        event = Event(event_type, data)
        self.history.append(event)
        
        try:
            # Handle priority handlers first
            for handler in self.priority_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"Priority handler error: {e}")
                    self.stats['handler_errors'] += 1
            
            # Handle regular async handlers
            async_tasks = [
                handler(event)
                for handler in self.async_subscribers[event_type]
            ]
            if async_tasks:
                await asyncio.gather(*async_tasks, return_exceptions=True)
            
            # Handle synchronous handlers
            for handler in self.sync_subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Sync handler error: {e}")
                    self.stats['handler_errors'] += 1
            
            self.stats['events_processed'] += 1
            event.handled = True
            
        except Exception as e:
            print(f"Event publishing error: {e}")
            self.stats['events_dropped'] += 1
            
    def get_recent_events(self, event_type=None, limit=10):
        """Get recent events, optionally filtered by type"""
        if event_type:
            events = [e for e in self.history if e.type == event_type]
        else:
            events = list(self.history)
        return events[-limit:]
    
    def get_stats(self):
        """Get event system statistics"""
        return {
            **self.stats,
            'subscribers': {
                'sync': {k: len(v) for k, v in self.sync_subscribers.items()},
                'async': {k: len(v) for k, v in self.async_subscribers.items()},
                'priority': {k: len(v) for k, v in self.priority_handlers.items()}
            }
        }
        
    def clear_history(self):
        """Clear event history"""
        self.history.clear()
        
    async def wait_for_event(self, event_type, timeout=None):
        """Wait for a specific event to occur"""
        future = asyncio.get_event_loop().create_future()
        
        def handler(event):
            if not future.done():
                future.set_result(event)
                
        self.subscribe(event_type, handler)
        
        try:
            return await asyncio.wait_for(future, timeout)
        finally:
            self.unsubscribe(event_type, handler)