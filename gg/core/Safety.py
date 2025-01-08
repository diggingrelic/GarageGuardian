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
        self.conditions = {}
        
    async def start(self):
        """Initialize the safety monitor"""
        return True
        
    def add_condition(self, name, check_func):
        """Add a safety condition to monitor"""
        self.conditions[name] = check_func
        
    async def check_safety(self):
        """Check all safety conditions"""
        results = {}
        for name, check in self.conditions.items():
            try:
                results[name] = await check()
            except Exception as e:
                results[name] = False
        return all(results.values())
        
    async def check_all(self):
        """Check all safety conditions and return detailed results"""
        results = {}
        for name, check in self.conditions.items():
            results[name] = await check()
        return results

    async def stop(self):
        """Stop the safety monitor"""
        return True
