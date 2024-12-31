from enum import Enum
import time
import asyncio
from typing import Callable, Dict, List

class SafetySeverity(Enum):
    CRITICAL = 0    # Immediate shutdown required
    HIGH = 1        # Requires immediate action
    MEDIUM = 2      # Requires attention
    LOW = 3         # Advisory only

class SafetyStatus(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    VIOLATION = "violation"
    FAILURE = "failure"

class SafetyCondition:
    def __init__(self, 
                 name: str,
                 check_func: Callable,
                 severity: SafetySeverity,
                 threshold: int = 1):  # Number of violations before triggering
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
        self.conditions: Dict[str, SafetyCondition] = {}
        self.event_system = event_system
        self.active = True
        self.last_check = 0
        self.check_interval = 1  # seconds
        self.violation_history = []
        self.max_history = 100
        
    def add_condition(self, 
                     name: str, 
                     check_func: Callable,
                     severity: SafetySeverity,
                     threshold: int = 1,
                     recovery_action: Callable = None):
        """Add a safety condition to monitor"""
        condition = SafetyCondition(name, check_func, severity, threshold)
        condition.recovery_action = recovery_action
        self.conditions[name] = condition

    async def check_safety(self) -> bool:
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
                print(f"Safety check error ({condition.name}): {e}")
                condition.status = SafetyStatus.FAILURE
                all_safe = False

        if violations:
            await self._handle_violations(violations)

        return all_safe

    async def _check_condition(self, condition: SafetyCondition) -> bool:
        """Check a single safety condition"""
        try:
            if asyncio.iscoroutinefunction(condition.check):
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
            raise Exception(f"Condition check error: {e}")

    async def _handle_violations(self, violations: List[SafetyCondition]):
        """Handle safety violations"""
        for condition in violations:
            # Log violation
            violation_record = {
                'name': condition.name,
                'severity': condition.severity.value,
                'timestamp': time.time(),
                'violation_count': condition.violation_count
            }
            self.violation_history.append(violation_record)
            if len(self.violation_history) > self.max_history:
                self.violation_history.pop(0)

            # Attempt recovery if action exists
            if condition.recovery_action:
                try:
                    if asyncio.iscoroutinefunction(condition.recovery_action):
                        await condition.recovery_action()
                    else:
                        condition.recovery_action()
                except Exception as e:
                    print(f"Recovery action error ({condition.name}): {e}")

            # Publish event
            if self.event_system:
                await self.event_system.publish(
                    'safety_violation',
                    {
                        'condition': condition.name,
                        'severity': condition.severity.value,
                        'status': condition.status.value,
                        'count': condition.violation_count
                    }
                )

    def get_status(self):
        """Get current safety status"""
        return {
            'active': self.active,
            'last_check': self.last_check,
            'conditions': {
                name: {
                    'status': cond.status.value,
                    'severity': cond.severity.value,
                    'violations': cond.violation_count,
                    'last_check': cond.last_check,
                    'last_violation': cond.last_violation
                }
                for name, cond in self.conditions.items()
            },
            'critical_conditions': [
                cond.name for cond in self.conditions.values()
                if cond.severity == SafetySeverity.CRITICAL and 
                cond.status == SafetyStatus.VIOLATION
            ]
        }

    def get_violations(self, limit=10):
        """Get recent violations"""
        return self.violation_history[-limit:]