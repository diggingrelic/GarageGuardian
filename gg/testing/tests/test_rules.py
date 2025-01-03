from ..microtest import TestCase
from ...core.Rules import (
    RulesEngine, Rule,
    PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_CRITICAL
)
from ...core.Events import EventSystem
import gc

class TestRules(TestCase):
    def setUp(self):
        """Initialize test components"""
        self.events = EventSystem()
        self.rules = RulesEngine(self.events)
        
    def tearDown(self):
        """Clean up after test"""
        self.rules = None
        self.events = None
        gc.collect()
        
    async def test_rule_creation(self):
        """Test rule creation and properties"""
        await self.rules.start()
        rule = Rule(
            name="test_rule",
            condition_func=lambda: True,
            action_func=lambda: None,
            priority=PRIORITY_HIGH
        )
        self.assertEqual(rule.name, "test_rule")
        self.assertEqual(rule.priority, PRIORITY_HIGH)
        self.assertTrue(rule.enabled)
        
    async def test_add_rule(self):
        """Test adding rules to engine"""
        await self.rules.start()
        self.rules.add_rule(
            name="test_rule",
            condition_func=lambda: True,
            action_func=lambda: None,
            priority=PRIORITY_HIGH
        )
        self.assertTrue("test_rule" in self.rules.rules)
        
    async def test_rule_evaluation(self):
        """Test rule evaluation and execution"""
        action_called = False
        
        async def test_action():
            nonlocal action_called
            action_called = True
            
        await self.rules.start()
        self.rules.add_rule(
            name="test_rule",
            condition_func=lambda: True,
            action_func=test_action
        )
        
        await self.rules.evaluate_all()
        self.assertTrue(action_called)
        
    async def test_rule_priority(self):
        """Test all rule priority levels"""
        for priority in [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_CRITICAL]:
            rule = Rule(
                name=f"test_priority_{priority}",
                condition_func=lambda: True,
                action_func=lambda: None,
                priority=priority
            )
            self.assertEqual(rule.priority, priority)
            
    async def test_rule_disable(self):
        """Test rule enabling/disabling"""
        self.rules.add_rule(
            name="test_rule",
            condition_func=lambda: True,
            action_func=lambda: None
        )
        
        self.rules.disable_rule("test_rule")
        self.assertFalse(self.rules.rules["test_rule"].enabled)
        
        self.rules.enable_rule("test_rule")
        self.assertTrue(self.rules.rules["test_rule"].enabled)