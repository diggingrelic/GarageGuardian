from micropython import const
import time
import asyncio

# Safety constants
MAX_CONDITIONS = const(20)
CHECK_TIMEOUT = const(500)
MAX_VIOLATIONS = const(3)

class SafetySeverity:
    CRITICAL = const(0)
    HIGH = const(1)
    MEDIUM = const(2)
    LOW = const(3)

class SafetyStatus:
    NORMAL = "normal"
    WARNING = "warning"
    VIOLATION = "violation"
    FAILURE = "failure"

class SafetyCondition:
    def __init__(self, name, check_func, severity, threshold=1):
        self.name = name
        self.check = check_func
        self.severity = severity
        self.threshold = threshold
        self.status = SafetyStatus.NORMAL
        self.violation_count = 0
        self.last_check = 0
        self.last_violation = None
        self.recovery_action = None

class SafetyMonitor:
    def __init__(self, event_system=None):
        self.conditions = {}
        self.event_system = event_system
        self.active = True
        self.last_check = 0
        self.check_interval = 1
        self.violation_history = []
        self.max_history = 20  # Reduced for memory constraints
        
    def add_condition(self, name, check_func, severity, threshold=1, recovery_action=None):
        """Add a safety condition to monitor"""
        if len(self.conditions) >= MAX_CONDITIONS:
            raise Exception("Maximum safety conditions reached")
            
        condition = SafetyCondition(name, check_func, severity, threshold)
        condition.recovery_action = recovery_action
        self.conditions[name] = condition

    async def check_safety(self):
        """Check all safety conditions"""
        if not self.active:
            return True

        current_time = time.time()
        if current_time - self.last_check < self.check_interval:
            return True

        self.last_check = current_time
        all_safe = True
        violations = []

        for condition in self.conditions.values():
            try:
                is_safe = await self._check_condition(condition)
                if not is_safe:
                    all_safe = False
                    violations.append(condition)
            except Exception as e:
                print("Safety check error:", e)
                condition.status = SafetyStatus.FAILURE
                all_safe = False

        if violations:
            await self._handle_violations(violations)

        return all_safe

    async def _check_condition(self, condition):
        """Check a single safety condition"""
        try:
            if hasattr(condition.check, '__await__'):
                is_safe = await condition.check()
            else:
                is_safe = condition.check()

            condition.last_check = time.time()

            if not is_safe:
                condition.violation_count += 1
                if condition.violation_count >= condition.threshold:
                    condition.status = SafetyStatus.VIOLATION
                    condition.last_violation = time.time()
                    return False
                else:
                    condition.status = SafetyStatus.WARNING
            else:
                condition.status = SafetyStatus.NORMAL
                condition.violation_count = 0

            return True

        except Exception as e:
            condition.status = SafetyStatus.FAILURE
            print("Condition check error:", e)
            return False

    async def _handle_violations(self, violations):
        """Handle safety violations"""
        for condition in violations:
            # Log violation with minimal data
            violation_record = {
                'name': condition.name,
                'severity': condition.severity,
                'time': time.time()
            }
            
            self.violation_history.append(violation_record)
            if len(self.violation_history) > self.max_history:
                self.violation_history.pop(0)

            # Attempt recovery
            if condition.recovery_action:
                try:
                    if hasattr(condition.recovery_action, '__await__'):
                        await condition.recovery_action()
                    else:
                        condition.recovery_action()
                except Exception as e:
                    print("Recovery action error:", e)

            # Publish event if available
            if self.event_system:
                await self.event_system.publish('safety_violation', {
                    'condition': condition.name,
                    'severity': condition.severity,
                    'status': condition.status
                })

    def get_status(self):
        """Get current safety status"""
        return {
            'active': self.active,
            'last_check': self.last_check,
            'conditions': {
                name: {
                    'status': cond.status,
                    'severity': cond.severity,
                    'violations': cond.violation_count
                }
                for name, cond in self.conditions.items()
            }
        }

    def get_violations(self, limit=5):
        """Get recent violations"""
        return self.violation_history[-limit:]

    def get_critical_conditions(self):
        """Get critical violations"""
        return [
            name for name, cond in self.conditions.items()
            if cond.status == SafetyStatus.VIOLATION and 
            cond.severity == SafetySeverity.CRITICAL
        ]