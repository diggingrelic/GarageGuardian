class SafetyCondition:
    def __init__(self, name, check_func, severity='warning'):
        self.name = name
        self.check = check_func
        self.severity = severity
        self.triggered = False

class SafetyMonitor:
    def __init__(self):
        self.conditions = {}
        self.critical_count = 0
        
    def add_condition(self, name, check_func, severity='warning'):
        """Add a safety condition to monitor"""
        self.conditions[name] = SafetyCondition(name, check_func, severity)
        
    async def check_safety(self):
        """Check all safety conditions"""
        all_safe = True
        self.critical_count = 0
        
        for condition in self.conditions.values():
            try:
                is_safe = condition.check()
                condition.triggered = not is_safe
                
                if not is_safe:
                    all_safe = False
                    if condition.severity == 'critical':
                        self.critical_count += 1
                        
            except Exception as e:
                print(f"Safety check error ({condition.name}): {e}")
                all_safe = False
                
        return all_safe
    
    def get_triggered_conditions(self):
        """Get list of triggered safety conditions"""
        return [cond.name for cond in self.conditions.values() 
                if cond.triggered]