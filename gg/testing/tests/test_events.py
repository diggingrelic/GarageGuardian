from ..microtest import TestCase
from ...core.Events import EventSystem, MAX_SUBSCRIBERS
import gc

class TestEvents(TestCase):
    def __init__(self):
        """Initialize the test case"""
        super().__init__()
        self.events = None
        
    def setUp(self):
        """Initialize test components"""
        self.events = EventSystem()
        
    def tearDown(self):
        """Clean up after test"""
        self.events = None
        gc.collect()
        
    async def test_handler(self):
        """Test event handler registration and execution"""
        handler_called = False
        
        async def test_handler(event):
            nonlocal handler_called
            handler_called = True
            self.assertEqual(event["type"], "test_event")
            
        self.events.subscribe("test_event", test_handler)
        await self.events.publish("test_event")
        self.assertTrue(handler_called)
        
    async def test_subscribe(self):
        """Test event subscription"""
        async def test_handler(event):
            pass
        result = self.events.subscribe("test_event", test_handler)
        self.assertTrue(result)
        self.assertTrue("test_event" in self.events.subscribers)
        
    async def test_subscribe_limit(self):
        """Test subscriber limit"""
        async def test_handler(event):
            pass
            
        # Add maximum number of subscribers
        for i in range(MAX_SUBSCRIBERS):
            result = self.events.subscribe("test_event", test_handler)
            self.assertTrue(result, f"Failed to add subscriber {i}")
            
        # Try to add one more (should fail)
        result = self.events.subscribe("test_event", test_handler)
        self.assertFalse(result)
        
    async def test_stats(self):
        """Test event statistics"""
        async def test_handler(event):
            pass
            
        self.events.subscribe("test_event", test_handler)
        await self.events.publish("test_event")
        
        self.assertEqual(self.events.stats["published"], 1)
        self.assertEqual(self.events.stats["handled"], 1)
        self.assertEqual(self.events.stats["errors"], 0)