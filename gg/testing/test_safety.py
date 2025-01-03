from .microtest import TestCase
from ..core.Safety import SafetyMonitor, SafetyCondition, SafetySeverity, SafetyStatus

class TestSafety(TestCase):
    def __init__(self):
        """Initialize test safety monitor"""
        super().__init__()
        self.safety = SafetyMonitor()
        self.violation_triggered = False
        
    def test_condition_creation(self):
        """Test safety condition creation and properties"""
        condition = SafetyCondition(
            name="test_condition",
            check_func=lambda: True,
            severity=SafetySeverity.HIGH
        )
        self.assertEqual(condition.name, "test_condition")
        self.assertEqual(condition.severity, SafetySeverity.HIGH)
        self.assertEqual(condition.status, SafetyStatus.NORMAL)
        
    def test_add_condition(self):
        """Test adding conditions to monitor"""
        self.safety.add_condition(
            name="test_condition",
            check_func=lambda: True,
            severity=SafetySeverity.HIGH
        )
        self.assertTrue("test_condition" in self.safety.conditions)
        
    async def test_check_safety(self):
        """Test safety checking functionality"""
        self.safety.add_condition(
            name="always_safe",
            check_func=lambda: True,
            severity=SafetySeverity.HIGH
        )
        result = await self.safety.check_safety()
        self.assertTrue(result)
        
    async def test_violation_handling(self):
        """Test violation detection and handling"""
        def on_violation():
            self.violation_triggered = True
            
        self.safety.add_condition(
            name="unsafe_condition",
            check_func=lambda: False,
            severity=SafetySeverity.CRITICAL,
            recovery_action=on_violation
        )
        
        result = await self.safety.check_safety()
        self.assertFalse(result)
        self.assertTrue(self.violation_triggered)
        
    async def test_emergency_stop(self):
        """Test emergency stop functionality"""
        self.stop_triggered = False
        
        def trigger_stop():
            self.stop_triggered = True
            
        self.safety.register_emergency_stop(trigger_stop)
        await self.safety.emergency_stop()
        self.assertTrue(self.stop_triggered)
        self.assertEqual(self.safety.status, SafetyStatus.FAILURE)
        
    def test_get_status(self):
        """Test status reporting"""
        self.safety.add_condition(
            name="test_condition",
            check_func=lambda: True,
            severity=SafetySeverity.HIGH
        )
        status = self.safety.get_status()
        self.assertTrue("test_condition" in status["conditions"])
        self.assertTrue("active" in status) 