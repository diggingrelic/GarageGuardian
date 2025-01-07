from ..microtest import TestCase
from ...interfaces.Relay import RelayDevice
from ..mocks.MockRelay import MockRelay
import gc

class TestRelayInterface(TestCase):
    def test_required_methods(self):
        """Verify required methods"""
        required_methods = [
            'activate',
            'deactivate',
            'is_active',
            'is_working'
        ]
        
        for method in required_methods:
            self.assertTrue(hasattr(RelayDevice, method))

class TestRelay(TestCase):
    def setUp(self):
        self.relay = MockRelay()
        
    def tearDown(self):
        self.relay = None
        gc.collect()
        
    async def test_activation(self):
        """Test basic relay activation"""
        self.assertFalse(await self.relay.is_active())
        await self.relay.activate()
        self.assertTrue(await self.relay.is_active())
        await self.relay.deactivate()
        self.assertFalse(await self.relay.is_active())
        
    async def test_error_handling(self):
        """Test relay error handling"""
        self.assertTrue(await self.relay.is_working())
        await self.relay.simulate_failure()
        await self.relay.simulate_failure()
        await self.relay.simulate_failure()
        self.assertFalse(await self.relay.is_working()) 