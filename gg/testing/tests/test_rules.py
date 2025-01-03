from ..microtest import TestCase
from ...core.Events import EventSystem
from ...core.Rules import Rule, RuleCondition, RulePriority, RuleStatus
import gc

class TestRules(TestCase):
    def __init__(self):
        super().__init__()
        self.events = EventSystem()
        self.rule_triggered = False
        
    def tearDown(self):
        self.events = EventSystem()
        self.rule_triggered = False
        gc.collect()
        
    def test_rule_creation(self):
        """Test rule creation and validation"""
        condition = RuleCondition(lambda: True, "test_event")
        rule = Rule(
            name="test_rule",
            conditions=condition,
            actions=lambda: setattr(self, 'rule_triggered', True),
            priority=RulePriority.HIGH
        )
        self.assertEqual(rule.status, RuleStatus.ACTIVE)
        self.assertEqual(rule.priority, RulePriority.HIGH)
        
    async def test_rule_evaluation(self):
        """Test rule evaluation and triggering"""
        condition = RuleCondition(lambda: True, "test_event")
        rule = Rule(
            name="test_rule",
            conditions=condition,
            actions=lambda: setattr(self, 'rule_triggered', True)
        )
        result = await rule.evaluate(self.events)
        self.assertTrue(result)
        self.assertTrue(self.rule_triggered)
        
    async def test_multiple_conditions(self):
        """Test rule with multiple conditions"""
        self.condition1_met = False
        self.condition2_met = False
        
        rule = Rule(
            name="test_multi",
            conditions=[
                RuleCondition(lambda: self.condition1_met, "event1"),
                RuleCondition(lambda: self.condition2_met, "event2")
            ],
            actions=lambda: setattr(self, 'rule_triggered', True),
            priority=RulePriority.CRITICAL,
            require_all=True
        )
        
        # Test with not all conditions met
        result = await rule.evaluate(self.events)
        self.assertFalse(result)
        
        # Test with all conditions met
        self.condition1_met = True
        self.condition2_met = True
        result = await rule.evaluate(self.events)
        self.assertTrue(result) 