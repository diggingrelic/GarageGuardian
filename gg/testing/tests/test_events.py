from ..microtest import TestCase
from ...core.Events import EventSystem, MAX_SUBSCRIBERS
import asyncio
import gc

class TestEvents(TestCase):
    def __init__(self):
        super().__init__()
        self.events = EventSystem()
        
    def tearDown(self):
        """Clean up after each test"""
        self.events = EventSystem()  # Create fresh instance for next test
        gc.collect()
        
    def test_handler(self):
        """Test event handler registration and execution"""
        handler_called = False
        
        def test_handler(event_name, event_data=None):
            nonlocal handler_called
            handler_called = True
            self.assertEqual(event_name.name, "test_event")
            
        self.events.subscribe("test_event", test_handler)
        asyncio.run(self.events.publish("test_event"))
        self.assertTrue(handler_called)
        
    def test_subscribe(self):
        """Test event subscription"""
        def test_handler(event_name, event_data=None):
            pass
        result = self.events.subscribe("test_event", test_handler)
        self.assertTrue(result)
        self.assertTrue("test_event" in self.events.subscribers)
        
    def test_subscribe_limit(self):
        """Test subscriber limit"""
        event_type = "test_event"
        
        # Add maximum number of subscribers
        for i in range(MAX_SUBSCRIBERS):
            def test_handler(event_name, event_data=None):
                pass
            result = self.events.subscribe(event_type, test_handler)
            self.assertTrue(result, f"Failed to add subscriber {i}")
            
        # Try to add one more (should return False)
        def one_more_handler(event_name, event_data=None):
            pass
        result = self.events.subscribe(event_type, one_more_handler)
        self.assertFalse(result, "Should not allow more than MAX_SUBSCRIBERS")
        
    async def test_publish(self):
        """Test event publishing"""
        test_data = []
        def test_handler(event_name, event_data):
            test_data.append(event_data)
            
        self.events.subscribe("test_event", test_handler)
        await self.events.publish("test_event", {"test": "data"})
        self.assertEqual(len(test_data), 1)
        self.assertEqual(test_data[0]["test"], "data")
        
    def test_stats(self):
        """Test event statistics"""
        stats = self.events.stats
        self.assertTrue('processed' in stats)
        self.assertTrue('dropped' in stats)
        self.assertTrue('errors' in stats)