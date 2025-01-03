from micropython import const #type: ignore

"""Safety severity levels"""
SAFETY_LOW = 1
SAFETY_MEDIUM = 2
SAFETY_HIGH = 3
SAFETY_CRITICAL = 4

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
    def __init__(self, name, check_func, severity=SAFETY_MEDIUM, recovery_action=None):
        self.name = name
        self.check_func = check_func
        self.severity = severity
        self.recovery_action = recovery_action
        self.status = SafetyStatus.NORMAL

class SafetyMonitor:
    """Safety monitoring system
    
    Tracks safety conditions and their states.
    Provides system-wide safety status monitoring.
    """
    
    def __init__(self):
        self.conditions = {}  # name -> SafetyCondition
        self._active = False
        self.status = SafetyStatus.NORMAL
        self._emergency_stop = None
        
    async def start(self):
        """Initialize the safety system"""
        self._active = True
        return True
        
    async def stop(self):
        """Clean shutdown of safety system"""
        self._active = False
        return True
        
    def add_condition(self, name, check_func, severity=SAFETY_MEDIUM, recovery_action=None):
        """Add a safety condition to monitor
        
        Args:
            name: Unique name for the condition
            check_func: Function that returns bool (True = safe)
            severity: Safety level (SAFETY_LOW to SAFETY_CRITICAL)
            recovery_action: Optional function to call when unsafe
        """
        condition = SafetyCondition(name, check_func, severity, recovery_action)
        self.conditions[name] = condition
        
    async def check_safety(self):
        """Check all safety conditions
        
        Returns:
            bool: True if all conditions are safe
        """
        if not self._active:
            return False
            
        all_safe = True
        for condition in self.conditions.values():
            try:
                if not condition.check_func():
                    all_safe = False
                    condition.status = SafetyStatus.FAILURE
                    if condition.recovery_action:
                        condition.recovery_action()
                else:
                    condition.status = SafetyStatus.NORMAL
            except Exception:
                all_safe = False
                condition.status = SafetyStatus.FAILURE
                
        return all_safe
        
    def register_emergency_stop(self, stop_func):
        """Register emergency stop callback"""
        self._emergency_stop = stop_func
        
    async def emergency_stop(self):
        """Trigger emergency stop"""
        if self._emergency_stop:
            await self._emergency_stop()
        self.status = SafetyStatus.FAILURE
        
    def get_status(self):
        """Get current safety status
        
        Returns:
            dict: Current safety system status
        """
        return {
            "active": self._active,
            "status": self.status,
            "conditions": {name: cond.status for name, cond in self.conditions.items()}
        }
