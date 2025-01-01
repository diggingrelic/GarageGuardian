from micropython import const
import time
import asyncio

# Rule constants
MAX_RULES = const(20)
EVAL_RETRY = const(3)
RULE_TIMEOUT = const(1000)

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

class Rule:
    def __init__(self, name, condition, action, priority=RulePriority.NORMAL, cooldown=0):
        self.name = name
        self.condition = condition
        self.action = action
        self.priority = priority
        self.cooldown = cooldown
        self.status = RuleStatus.ACTIVE
        self.last_triggered = 0
        self.trigger_count = 0
        self.last_error = None
        self.retry_count = 0

    def can_trigger(self):
        """Check if rule can trigger based on cooldown"""
        if self.status == RuleStatus.DISABLED:
            return False
        return (time.time() - self.last_triggered) > self.cooldown

class RulesEngine:
    def __init__(self, event_system=None):
        self.rules = []
        self.event_system = event_system
        self.active = True
        self.last_evaluation = None
        self.eval_lock = False

    def add_rule(self, name, condition, action, priority=RulePriority.NORMAL, cooldown=0):
        """Add a new rule to the engine"""
        if len(self.rules) >= MAX_RULES:
            raise Exception("Maximum rules limit reached")
            
        rule = Rule(name, condition, action, priority, cooldown)
        self.rules.append(rule)
        # Sort rules by priority
        self.rules.sort(key=lambda x: x.priority)
        return rule

    def remove_rule(self, name):
        """Remove a rule by name"""
        initial_length = len(self.rules)
        self.rules = [r for r in self.rules if r.name != name]
        return len(self.rules) < initial_length

    def disable_rule(self, name):
        """Disable a rule temporarily"""
        for rule in self.rules:
            if rule.name == name:
                rule.status = RuleStatus.DISABLED
                return True
        return False

    def enable_rule(self, name):
        """Re-enable a disabled rule"""
        for rule in self.rules:
            if rule.name == name:
                rule.status = RuleStatus.ACTIVE
                rule.retry_count = 0
                return True
        return False

    async def evaluate_rules(self):
        """Evaluate all active rules"""
        if not self.active or self.eval_lock:
            return

        try:
            self.eval_lock = True
            self.last_evaluation = time.time()
            
            for rule in self.rules:
                if not rule.can_trigger():
                    continue

                try:
                    if await self._evaluate_condition(rule):
                        await self._execute_action(rule)
                except Exception as e:
                    await self._handle_rule_error(rule, str(e))

        finally:
            self.eval_lock = False

    async def _evaluate_condition(self, rule):
        """Evaluate a rule's condition"""
        try:
            if hasattr(rule.condition, '__await__'):
                result = await rule.condition()
            else:
                result = rule.condition()
            
            rule.retry_count = 0
            return bool(result)
            
        except Exception as e:
            print("Condition error:", e)
            return False

    async def _execute_action(self, rule):
        """Execute a rule's action"""
        try:
            if hasattr(rule.action, '__await__'):
                await rule.action()
            else:
                rule.action()
            
            rule.last_triggered = time.time()
            rule.trigger_count += 1
            rule.status = RuleStatus.TRIGGERED

            if self.event_system:
                await self.event_system.publish('rule_triggered', {
                    'rule': rule.name,
                    'count': rule.trigger_count,
                    'priority': rule.priority
                })
                
        except Exception as e:
            raise Exception(f"Action error: {e}")

    async def _handle_rule_error(self, rule, error):
        """Handle rule execution error"""
        rule.last_error = error
        rule.retry_count += 1
        
        if rule.retry_count >= EVAL_RETRY:
            rule.status = RuleStatus.FAILED
            if self.event_system:
                await self.event_system.publish('rule_error', {
                    'rule': rule.name,
                    'error': error
                })

    def get_rule_status(self, name=None):
        """Get status of one or all rules"""
        if name:
            for rule in self.rules:
                if rule.name == name:
                    return self._get_rule_state(rule)
            return None
        
        return [self._get_rule_state(rule) for rule in self.rules]

    def _get_rule_state(self, rule):
        """Get state of a single rule"""
        return {
            'name': rule.name,
            'status': rule.status,
            'priority': rule.priority,
            'triggers': rule.trigger_count,
            'last_triggered': rule.last_triggered,
            'last_error': rule.last_error
        }