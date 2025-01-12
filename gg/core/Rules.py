from micropython import const # type: ignore
from ..logging.Log import debug, error

# Rule system constants
MAX_RULES = const(20)

# Rule priority levels
PRIORITY_LOW = const(1)
PRIORITY_MEDIUM = const(2)
PRIORITY_HIGH = const(3)
PRIORITY_CRITICAL = const(4)

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
    """Base class for all rules"""
    def __init__(self):
        self.name = self.__class__.__name__
        self.enabled = True
        self.subscriptions = set()
        
    def subscribe_to(self, event_type):
        """Subscribe to an event type"""
        self.subscriptions.add(event_type)

class RulesEngine:
    """Rules processing engine"""
    def __init__(self, event_system):
        self.rules = {}  # name -> Rule
        self.events = event_system
        self._active = False
        
    async def start(self):
        """Start the rules engine"""
        self._active = True
        debug("Rules engine started")
        return True
        
    async def stop(self):
        """Stop the rules engine"""
        self._active = False
        debug("Rules engine stopped")
        return True
        
    async def add_rule(self, rule):
        """Add a new rule"""
        self.rules[rule.name] = rule
        debug(f"Added rule: {rule.name}")
        
    async def remove_rule(self, name):
        """Remove a rule"""
        if name in self.rules:
            del self.rules[name]
            debug(f"Removed rule: {name}")
            
    async def evaluate_all(self, event=None):
        """Evaluate all rules"""
        if not self._active:
            return
            
        for rule in list(self.rules.values()):
            if rule.enabled:
                # Check if rule subscribes to this event type
                if event and hasattr(event, 'type') and \
                   rule.subscriptions and \
                   event.type not in rule.subscriptions:
                    continue
                    
                try:
                    if await rule.evaluate(event):
                        await self.remove_rule(rule.name)
                except Exception as e:
                    error(f"Rule evaluation failed: {e}")