class MockPin:
    OUT = 'out'
    IN = 'in'
    
    def __init__(self, pin, mode):
        self.pin = pin
        self.mode = mode
        self._value = 0

    def value(self, val=None):
        if val is not None:
            self._value = val
        return self._value

    def toggle(self):
        self._value = not self._value 