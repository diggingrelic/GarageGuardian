from micropython import const # type: ignore
import asyncio
from ..logging.Log import debug, error
import time

# Rule system constants
MAX_RULES = const(20)

# Rule priority levels
PRIORITY_LOW = 1
PRIORITY_MEDIUM = 2
PRIORITY_HIGH = 3
PRIORITY_CRITICAL = 4

class RulePriority:
    """Rule priority levels
    
    Defines the priority levels for rules, from lowest (LOW)
    to highest (CRITICAL). Higher priority rules are evaluated first.
    """
    LOW = const(0)
    MEDIUM = const(1)
    HIGH = const(2)
    CRITICAL = const(3)

class RuleStatus:
    """Rule status indicators
    
    Defines the possible states of a rule in the system.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    ERROR = "error"

class RuleCondition:
    """A condition that must be met for a rule to trigger
    
    Represents a single condition with its check function and
    associated event type.
    
    Attributes:
        check_func (callable): Function that returns True if condition is met
        event_type (str): Type of event this condition responds to
        last_check (float): Timestamp of last check
        last_result (bool): Result of last check
    """
    def __init__(self, check_func, event_type=None):
        self.check = check_func
        self.event_type = event_type
        self.last_check = 0
        self.last_result = False

class Rule:
    """Represents a system rule with conditions and actions"""
    
    def __init__(self, name: str, condition_func, action_func, priority=PRIORITY_MEDIUM):
        self.name = name
        self.condition_func = condition_func
        self.action_func = action_func
        self.priority = priority
        self.last_run = 0
        self.enabled = True

class RulesEngine:
    """Rules processing engine"""
    
    def __init__(self, event_system):
        self.rules = {}  # name -> Rule
        self.events = event_system
        self._active = False
        
    async def start(self):
        """Initialize the rules engine"""
        self._active = True
        return True
        
    async def stop(self):
        """Clean shutdown of rules engine"""
        self._active = False
        return True
        
    def add_rule(self, name: str, condition_func, action_func, priority=PRIORITY_MEDIUM):
        """Add a new rule
        
        Args:
            name: Unique rule identifier
            condition_func: Function that returns bool when rule should trigger
            action_func: Async function to execute when rule triggers
            priority: Rule priority level
        """
        rule = Rule(name, condition_func, action_func, priority)
        self.rules[name] = rule
        
    async def evaluate_all(self):
        """Evaluate and execute all active rules
        
        Rules are processed in priority order (highest first)
        """
        if not self._active:
            return
            
        # Sort rules by priority
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: r.priority,
            reverse=True
        )
        
        # Evaluate rules
        for rule in sorted_rules:
            if not rule.enabled:
                continue
                
            try:
                if rule.condition_func():
                    await rule.action_func()
                    rule.last_run = time.time()
                    await self.events.publish("rule_triggered", {
                        "name": rule.name,
                        "priority": rule.priority
                    })
            except Exception as e:
                await self.events.publish("rule_error", {
                    "name": rule.name,
                    "error": str(e)
                })
                
    def disable_rule(self, name: str):
        """Disable a rule"""
        if name in self.rules:
            self.rules[name].enabled = False
            
    def enable_rule(self, name: str):
        """Enable a rule"""
        if name in self.rules:
            self.rules[name].enabled = True
            
    def get_status(self):
        """Get rules engine status
        
        Returns:
            dict: Current rules status
        """
        return {
            "active": self._active,
            "rules": {
                name: {
                    "enabled": rule.enabled,
                    "priority": rule.priority,
                    "last_run": rule.last_run
                }
                for name, rule in self.rules.items()
            }
        }