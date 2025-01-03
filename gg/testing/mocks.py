class MockPin:
    """Mock implementation of machine.Pin"""
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2
    ALT = 3
    PULL_UP = 1
    PULL_DOWN = 2
    
    def __init__(self, id, mode=-1, pull=-1):
        self.id = id
        self._mode = mode
        self._pull = pull
        self._value = 0
        
    def init(self, mode=-1, pull=-1):
        self._mode = mode
        self._pull = pull
        
    def value(self, val=None):
        if val is not None:
            self._value = val
        return self._value
        
    def mode(self):
        return self._mode 