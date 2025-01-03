class PinInterface:
    """Hardware abstraction for digital pins"""
    def __init__(self, pin_id):
        self.pin_id = pin_id
        
    def set_high(self):
        """Set pin high"""
        raise NotImplementedError
        
    def set_low(self):
        """Set pin low"""
        raise NotImplementedError
        
    def read(self):
        """Read pin state"""
        raise NotImplementedError
        
    def cleanup(self):
        """Cleanup pin resources"""
        pass

class DoorInterface:
    """Hardware abstraction for garage door"""
    def __init__(self):
        self.relay = None
        self.position_sensor = None
        self.obstruction_sensor = None
        
    async def open(self):
        """Start door opening"""
        raise NotImplementedError
        
    async def close(self):
        """Start door closing"""
        raise NotImplementedError
        
    async def stop(self):
        """Stop door movement"""
        raise NotImplementedError
        
    def is_fully_open(self):
        """Check if door is fully open"""
        raise NotImplementedError
        
    def is_fully_closed(self):
        """Check if door is fully closed"""
        raise NotImplementedError
        
    def is_obstructed(self):
        """Check if door path is obstructed"""
        raise NotImplementedError