import unittest
from gg.core.Events import EventSystem

class TestEvents(unittest.TestCase):
    def setUp(self):
        self.events = EventSystem()
        self.test_data = []

    async def async_test_handler(self, event):
        self.test_data.append(event.data)

    def test_handler(self, event):
        self.test_data.append(event.data)

    def test_subscribe(self):
        """Test event subscription"""
        result = self.events.subscribe("test_event", self.test_handler)
        self.assertTrue(result)
        self.assertIn("test_event", self.events.subscribers)

    async def test_publish(self):
        """Test event publishing"""
        self.events.subscribe("test_event", self.test_handler)
        await self.events.publish("test_event", {"test": "data"})
        self.assertEqual(self.test_data[0]["test"], "data") 