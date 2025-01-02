from micropython import const # type: ignore
import time
import asyncio

# Rule constants
MAX_RULES = const(20)
MAX_CONDITIONS = const(5)
EVAL_RETRY = const(3)
RULE_TIMEOUT = const(1000)  # ms

class RulePriority:
    CRITICAL = const(0)
    HIGH = const(1)
    NORMAL = const(2)
    LOW = const(3)

class RuleStatus:
    ACTIVE = "active"
    DISABLED = "disabled"
    TRIGGERED = "triggered"
    FAILED = "failed"
    COOLDOWN = "cooldown"

class RuleCondition:
    def __init__(self, check_func, event_type=None):
        self.check = check_func  # Function that returns bool
        self.event_type = event_type  # Optional event trigger
        self.last_check = 0
        self.last_value = False

class Rule:
    def __init__(self, name, conditions, actions, priority=RulePriority.NORMAL, 
                 cooldown=0, require_all=True):
        self.name = name
        self.conditions = []  # List of RuleCondition objects
        self.actions = actions if isinstance(actions, list) else [actions]
        self.priority = priority
        self.cooldown = cooldown
        self.require_all = require_all  # True=AND, False=OR
        self.status = RuleStatus.ACTIVE
        self.last_triggered = 0
        self.trigger_count = 0
        self.last_error = None
        self.retry_count = 0
        self.event_triggers = set()  # Track which events can trigger this rule
        
        # Setup conditions
        for condition in conditions if isinstance(conditions, list) else [conditions]:
            if isinstance(condition, RuleCondition):
                self.conditions.append(condition)
                if condition.event_type:
                    self.event_triggers.add(condition.event_type)
            else:
                # Convert simple function to RuleCondition
                self.conditions.append(RuleCondition(condition))

    def can_trigger(self):
        """Check if rule can trigger based on status and cooldown"""
        if self.status == RuleStatus.DISABLED:
            return False
        if self.status == RuleStatus.COOLDOWN:
            if (time.time() - self.last_triggered) > self.cooldown:
                self.status = RuleStatus.ACTIVE
            else:
                return False
        return True

    async def evaluate(self, event_system, event_type=None):
        """Evaluate rule conditions and execute actions if met"""
        if not self.can_trigger():
            return False

        try:
            # If event_type provided, only check conditions for that event
            conditions_met = 0
            for condition in self.conditions:
                if event_type and condition.event_type != event_type:
                    continue
                    
                # Check condition
                try:
                    result = await condition.check(event_system) if asyncio.iscoroutinefunction(condition.check) else condition.check()
                    condition.last_check = time.time()
                    condition.last_value = result
                    if result:
                        conditions_met += 1
                except Exception as e:
                    self.last_error = str(e)
                    return False

            # Determine if rule should trigger
            should_trigger = (conditions_met == len(self.conditions) if self.require_all 
                            else conditions_met > 0)

            if should_trigger:
                # Execute all actions
                for action in self.actions:
                    try:
                        if asyncio.iscoroutinefunction(action):
                            await action(event_system)
                        else:
                            action()
                    except Exception as e:
                        self.last_error = str(e)
                        self.status = RuleStatus.FAILED
                        return False

                self.last_triggered = time.time()
                self.trigger_count += 1
                self.status = RuleStatus.COOLDOWN if self.cooldown > 0 else RuleStatus.ACTIVE
                return True

        except Exception as e:
            self.last_error = str(e)
            self.status = RuleStatus.FAILED
            return False

        return False

    def get_state(self):
        """Get current rule state"""
        return {
            "name": self.name,
            "status": self.status,
            "priority": self.priority,
            "last_triggered": self.last_triggered,
            "trigger_count": self.trigger_count,
            "last_error": self.last_error,
            "conditions_met": [c.last_value for c in self.conditions]
        }

class RulesEngine:
    def __init__(self, event_system):
        self.rules = []
        self.events = event_system
        self.active = True
        self.stats = {
            'evaluated': 0,
            'triggered': 0,
            'errors': 0
        }

    async def add_rule(self, rule):
        """Add a rule and subscribe to its events"""
        if len(self.rules) >= MAX_RULES:
            return False
            
        self.rules.append(rule)
        # Subscribe to all events that could trigger this rule
        for event_type in rule.event_triggers:
            self.events.subscribe(event_type, 
                                lambda e: self._handle_event(e, rule))
        return True

    async def _handle_event(self, event, rule):
        """Handle an event by evaluating the relevant rule"""
        if not self.active:
            return
            
        try:
            self.stats['evaluated'] += 1
            if await rule.evaluate(self.events, event.type):
                self.stats['triggered'] += 1
        except Exception as e:
            self.stats['errors'] += 1
            self.last_error = str(e)