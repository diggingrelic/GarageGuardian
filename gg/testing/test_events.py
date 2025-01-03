from .microtest import TestCase
from ..core.Events import EventSystem, MAX_SUBSCRIBERS

class TestEvents(TestCase):
    def __init__(self):
        super().__init__()
        self.events = EventSystem()
        self.test_data = []
        self.handler_called = False

    def test_handler(self, event):
        self.test_data.append(event.data)
        self.handler_called = True

    def test_subscribe(self):
        """Test event subscription"""
        result = self.events.subscribe("test_event", self.test_handler)
        self.assertTrue(result)
        self.assertIn("test_event", self.events.subscribers)

    def test_subscribe_limit(self):
        """Test subscriber limit"""
        # Add maximum number of subscribers to a single event type (19 subscribers)
        event_type = "test_event"
        for i in range(MAX_SUBSCRIBERS - 1):  # One less than MAX_SUBSCRIBERS
            result = self.events.subscribe(event_type, lambda e: None)
            self.assertTrue(result, f"Failed to add subscriber {i}")
        
        # Add the last subscriber (number 20)
        result = self.events.subscribe(event_type, lambda e: None)
        self.assertTrue(result, "Failed to add final subscriber")
        
        # Try to add one more (should fail)
        result = self.events.subscribe(event_type, lambda e: None)
        self.assertFalse(result, "Should not allow more than MAX_SUBSCRIBERS")

    async def test_publish(self):
        """Test event publishing"""
        self.test_data = []
        self.handler_called = False
        self.events.subscribe("test_event", self.test_handler)
        await self.events.publish("test_event", {"test": "data"})
        self.assertTrue(self.handler_called)
        self.assertEqual(self.test_data[0]["test"], "data")

    async def test_multiple_subscribers(self):
        """Test multiple subscribers for same event"""
        self.test_data = []
        self.events.subscribe("multi_event", self.test_handler)
        self.events.subscribe("multi_event", lambda e: self.test_data.append({"second": True}))
        await self.events.publish("multi_event", {"first": True})
        self.assertEqual(len(self.test_data), 2)

    def test_get_stats(self):
        """Test event statistics"""
        stats = self.events.get_stats()
        self.assertTrue('processed' in stats)
        self.assertTrue('dropped' in stats)
        self.assertTrue('errors' in stats)

    async def test_state_transitions(self):
        """Test system state transitions"""
        # Test initial state
        self.test_data = []
        self.events.subscribe("system_state", self.test_handler)
        
        # Test state change
        await self.events.publish("system_state", {"state": "ready"})
        self.assertEqual(self.test_data[0]["state"], "ready")
        
        # Test another state change
        await self.events.publish("system_state", {"state": "running"})
        self.assertEqual(self.test_data[1]["state"], "running")