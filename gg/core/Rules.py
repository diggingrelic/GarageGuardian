from micropython import const # type: ignore
import asyncio
from ..logging.Log import debug, error

# Rule system constants
MAX_RULES = const(20)

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
    """A rule that can trigger actions based on conditions
    
    Rules combine conditions and actions with priority levels to
    create automated responses to system events.
    
    Attributes:
        name (str): Name of the rule
        conditions (list): List of RuleConditions to check
        actions (callable): Function to call when rule triggers
        priority (RulePriority): Priority level of the rule
        status (RuleStatus): Current status of the rule
        require_all (bool): Whether all conditions must be met
        
    Example:
        >>> def temp_high(): return sensor.temp > 30
        >>> def fan_on(): fan.start()
        >>> rule = Rule("high_temp", temp_high, fan_on, RulePriority.HIGH)
    """
    def __init__(self, name, conditions, actions, priority=RulePriority.LOW, require_all=True):
        self.name = name
        self.conditions = conditions if isinstance(conditions, list) else [conditions]
        self.actions = actions
        self.priority = priority
        self.status = RuleStatus.ACTIVE
        self.require_all = require_all
        self.last_triggered = 0

    async def evaluate(self, event_system):
        """Evaluate the rule's conditions and trigger actions if met
        
        Args:
            event_system (EventSystem): System for publishing events
            
        Returns:
            bool: True if rule triggered, False otherwise
            
        Example:
            >>> triggered = await rule.evaluate(event_system)
            >>> if triggered:
            ...     print("Rule activated")
        """
        if self.status != RuleStatus.ACTIVE:
            return False
            
        try:
            conditions_met = 0
            for condition in self.conditions:
                if condition.check():
                    conditions_met += 1
                    if not self.require_all:
                        break
                        
            should_trigger = (conditions_met == len(self.conditions)) if self.require_all else (conditions_met > 0)
            
            if should_trigger:
                if asyncio.iscoroutinefunction(self.actions):
                    await self.actions()
                else:
                    self.actions()
                return True
                    
        except Exception as e:
            error(f"Rule evaluation failed for {self.name}: {e}")
            self.status = RuleStatus.ERROR
            
        return False

class RulesEngine:
    """Engine for managing and evaluating rules
    
    Manages a collection of rules, evaluating them based on
    priority and handling rule-triggered events.
    
    Attributes:
        rules (dict): Dictionary of active rules
        event_system (EventSystem): System for handling events
        
    Example:
        >>> engine = RulesEngine(event_system)
        >>> engine.add_rule(Rule("temp_control", temp_check, fan_control))
    """
    def __init__(self, event_system):
        self.rules = {}
        self.event_system = event_system
        
    def add_rule(self, rule):
        """Add a rule to the engine
        
        Args:
            rule (Rule): Rule to add
            
        Returns:
            bool: True if added successfully, False if at limit
            
        Example:
            >>> rule = Rule("door_check", door_sensor, door_alarm)
            >>> engine.add_rule(rule)
        """
        if len(self.rules) >= MAX_RULES:
            return False
        self.rules[rule.name] = rule
        return True
        
    async def evaluate_all(self):
        """Evaluate all active rules
        
        Evaluates rules in priority order, triggering actions
        as needed.
        
        Returns:
            int: Number of rules triggered
            
        Example:
            >>> triggered = await engine.evaluate_all()
            >>> print(f"{triggered} rules activated")
        """
        triggered = 0
        # Sort rules by priority
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            if await rule.evaluate(self.event_system):
                triggered += 1
                debug(f"Rule triggered: {rule.name}")
                
        return triggered