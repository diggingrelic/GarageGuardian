from ..microtest import TestCase
from ...core.Safety import (
    SafetyMonitor, SafetyCondition, SafetyStatus,
    SAFETY_LOW, SAFETY_MEDIUM, SAFETY_HIGH, SAFETY_CRITICAL
)
import gc

class TestSafety(TestCase):
    def setUp(self):
        """Initialize test components"""
        self.safety = SafetyMonitor()
        
    def tearDown(self):
        """Clean up after test"""
        self.safety = None
        gc.collect()
        
    async def test_condition_creation(self):
        """Test safety condition creation and properties"""
        condition = SafetyCondition(
            name="test_condition",
            check_func=lambda: True,
            severity=SAFETY_HIGH
        )
        self.assertEqual(condition.name, "test_condition")
        self.assertEqual(condition.severity, SAFETY_HIGH)
        self.assertEqual(condition.status, SafetyStatus.NORMAL)
        
    async def test_add_condition(self):
        """Test adding conditions to monitor"""
        await self.safety.start()  # Need to start before adding conditions
        self.safety.add_condition(
            name="test_condition",
            check_func=lambda: True,
            severity=SAFETY_HIGH
        )
        self.assertTrue("test_condition" in self.safety.conditions)
        
    async def test_check_safety(self):
        """Test safety checking functionality"""
        await self.safety.start()
        self.safety.add_condition(
            name="always_safe",
            check_func=lambda: True,
            severity=SAFETY_HIGH
        )
        result = await self.safety.check_safety()
        self.assertTrue(result)
        
    async def test_safety_levels(self):
        """Test all safety levels"""
        await self.safety.start()
        for level in [SAFETY_LOW, SAFETY_MEDIUM, SAFETY_HIGH, SAFETY_CRITICAL]:
            condition = SafetyCondition(
                name=f"test_level_{level}",
                check_func=lambda: True,
                severity=level
            )
            self.assertEqual(condition.severity, level) 