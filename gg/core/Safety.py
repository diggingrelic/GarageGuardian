from micropython import const #type: ignore
import time
import asyncio
from ..logging.Log import error, critical

# Safety system constants
MAX_CONDITIONS = const(20)

class SafetySeverity:
    """Safety severity levels for conditions
    
    Defines the severity levels for safety conditions, from lowest (LOW)
    to highest (CRITICAL).
    """
    LOW = const(0)
    MEDIUM = const(1)
    HIGH = const(2)
    CRITICAL = const(3)

class SafetyStatus:
    """Safety system status indicators
    
    Defines the possible states of the safety monitoring system.
    """
    NORMAL = "normal"
    WARNING = "warning"
    VIOLATION = "violation"
    FAILURE = "failure"

class SafetyCondition:
    """A safety condition to be monitored
    
    Represents a single safety condition with its check function,
    severity level, and current status.
    
    Attributes:
        name (str): Name of the safety condition
        check_func (callable): Function that returns True if condition is safe
        severity (SafetySeverity): Severity level of the condition
        status (SafetyStatus): Current status of the condition
        threshold (int): Number of violations before triggering
        violation_count (int): Current number of violations
        recovery_action (callable, optional): Function to call when violated
    """
    def __init__(self, name, check_func, severity, threshold=1):
        self.name = name
        self.check = check_func
        self.severity = severity
        self.status = SafetyStatus.NORMAL
        self.threshold = threshold
        self.violation_count = 0
        self.recovery_action = None

class SafetyMonitor:
    """Safety monitoring system
    
    Monitors safety conditions and triggers appropriate responses
    when violations occur.
    
    Attributes:
        conditions (dict): Dictionary of safety conditions
        event_system (EventSystem): Optional event system for notifications
        active (bool): Whether the monitor is active
        status (SafetyStatus): Overall system safety status
        violation_history (list): History of safety violations
        emergency_stops (list): List of emergency stop functions
        
    Example:
        >>> safety = SafetyMonitor()
        >>> safety.add_condition("temp_check", 
        ...     lambda: sensor.temp < 50, 
        ...     SafetySeverity.HIGH)
    """
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
        """Register an emergency stop function
        
        Args:
            stop_func (callable): Function to call during emergency stop
            
        Example:
            >>> safety.register_emergency_stop(motor.emergency_stop)
        """
        self.emergency_stops.append(stop_func)
        
    async def emergency_stop(self):
        """Trigger emergency stop
        
        Calls all registered emergency stop functions and
        sets system to failure state.
        
        Example:
            >>> await safety.emergency_stop()
            >>> assert safety.status == SafetyStatus.FAILURE
        """
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
        """Add a safety condition to monitor
        
        Args:
            name (str): Name of the condition
            check_func (callable): Function that returns True if condition is safe
            severity (SafetySeverity): Severity level
            threshold (int, optional): Violations before triggering. Defaults to 1
            recovery_action (callable, optional): Function to call when violated
            
        Raises:
            Exception: If maximum conditions reached
            
        Example:
            >>> safety.add_condition("door_sensor",
            ...     lambda: not door.is_obstructed(),
            ...     SafetySeverity.HIGH,
            ...     recovery_action=door.stop)
        """
        if len(self.conditions) >= MAX_CONDITIONS:
            error("Maximum safety conditions reached")
            raise Exception("Maximum safety conditions reached")
            
        condition = SafetyCondition(name, check_func, severity, threshold)
        condition.recovery_action = recovery_action
        self.conditions[name] = condition
        
    async def check_safety(self):
        """Check all safety conditions
        
        Evaluates all registered safety conditions and triggers
        appropriate responses for any violations.
        
        Returns:
            bool: True if all conditions are safe, False otherwise
            
        Example:
            >>> is_safe = await safety.check_safety()
            >>> if not is_safe:
            ...     print("Safety violation detected")
        """
        if not self.active:
            return False
            
        all_safe = True
        for name, condition in self.conditions.items():
            try:
                is_safe = condition.check()
                if not is_safe:
                    all_safe = False
                    condition.violation_count += 1
                    if condition.violation_count >= condition.threshold:
                        await self._handle_violation(condition)
                else:
                    condition.violation_count = 0
            except Exception as e:
                error(f"Safety check failed for {name}: {e}")
                all_safe = False
                
        return all_safe
        
    async def _handle_violation(self, condition):
        """Handle a safety condition violation
        
        Args:
            condition (SafetyCondition): The violated condition
            
        Internal method to process violations and trigger recovery actions.
        """
        violation = {
            "condition": condition.name,
            "severity": condition.severity,
            "timestamp": time.time()
        }
        self.violation_history.append(violation)
        if len(self.violation_history) > self.max_history:
            self.violation_history.pop(0)
            
        if condition.severity >= SafetySeverity.HIGH:
            await self.emergency_stop()
        elif condition.recovery_action:
            try:
                if asyncio.iscoroutinefunction(condition.recovery_action):
                    await condition.recovery_action()
                else:
                    condition.recovery_action()
            except Exception as e:
                error(f"Recovery action failed for {condition.name}: {e}")

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
