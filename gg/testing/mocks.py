class MockPin:
    """Mock Pin class for testing"""
    IN = 0
    OUT = 1
    
    def __init__(self, pin_number, mode, pull=None):
        self.pin_number = pin_number
        self.mode = mode
        self.pull = pull
        self._value = 0
        
    def value(self, val=None):
        if val is not None:
            self._value = val
        return self._value
        
    def on(self):
        self._value = 1
        
    def off(self):
        self._value = 0 