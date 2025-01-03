from micropython import const #type: ignore
import time
import asyncio
from ..logging.Log import debug, info, warning, error, critical

# Safety constants
MAX_CONDITIONS = const(20)
CHECK_TIMEOUT = const(500)  # ms
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
        self.status = SafetyStatus.NORMAL
        self.last_check = 0
        self.check_interval = 1
        self.violation_history = []
        self.max_history = 20
        self.emergency_stops = []
        
    def register_emergency_stop(self, stop_func):
        """Register an emergency stop function"""
        self.emergency_stops.append(stop_func)
        
    async def emergency_stop(self):
        """Trigger emergency stop"""
        critical("EMERGENCY STOP TRIGGERED")
        self.status = SafetyStatus.FAILURE
        self.active = False
        
        for stop_func in self.emergency_stops:
            try:
                if asyncio.iscoroutinefunction(stop_func):
                    await stop_func()
                else:
                    stop_func()
            except Exception as e:
                error(f"Emergency stop function failed: {e}")
                
    def add_condition(self, name, check_func, severity, threshold=1, recovery_action=None):
        """Add a safety condition to monitor"""
        if len(self.conditions) >= MAX_CONDITIONS:
            error("Maximum safety conditions reached")
            raise Exception("Maximum safety conditions reached")
            
        condition = SafetyCondition(name, check_func, severity, threshold)
        condition.recovery_action = recovery_action
        self.conditions[name] = condition
        debug(f"Safety condition added: {name}")

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
                    if condition.severity == SafetySeverity.CRITICAL:
                        await self.emergency_stop()
            except Exception as e:
                error(f"Safety check error: {e}")
                condition.status = SafetyStatus.FAILURE
                all_safe = False

        if violations:
            await self._handle_violations(violations)

        return all_safe

    async def _check_condition(self, condition):
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
                    warning(f"Safety violation: {condition.name}")
                    return False
                else:
                    condition.status = SafetyStatus.WARNING
                    info(f"Safety warning: {condition.name}")
            else:
                condition.status = SafetyStatus.NORMAL
                condition.violation_count = 0

            return True

        except Exception as e:
            error(f"Condition check error: {e}")
            condition.status = SafetyStatus.FAILURE
            return False

    async def _handle_violations(self, violations):
        """Handle safety violations"""
        for condition in violations:
            # Log violation
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
                    if asyncio.iscoroutinefunction(condition.recovery_action):
                        await condition.recovery_action()
                    else:
                        condition.recovery_action()
                except Exception as e:
                    error(f"Recovery action error: {e}")

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
            'status': self.status,
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