from machine import Pin # type: ignore
from .MachineHAL import MachinePin
from ..logging.Log import error

class GPIOManager:
    """Manages GPIO pins and abstracts hardware details"""
    
    # Pin modes
    IN = Pin.IN
    OUT = Pin.OUT
    
    def __init__(self, hardware_interface=MachinePin):
        """Initialize with hardware interface (default=MachinePin, can be mocked)"""
        self.pins = {}
        self._hardware = hardware_interface
        
    def setup(self, name: str, pin_number: int, mode: int, pull=None) -> bool:
        """Setup a named GPIO pin"""
        try:
            pin = self._hardware(pin_number, mode)
            self.pins[name] = pin
            return True
        except Exception as e:
            error(f"GPIO setup failed for {name}: {e}")
            return False
            
    def write(self, name: str, state: bool) -> bool:
        """Set pin state (True=High, False=Low)"""
        pin = self.pins.get(name)
        if pin:
            try:
                if state:
                    pin.set_high()
                else:
                    pin.set_low()
                return True
            except Exception as e:
                error(f"GPIO write failed for {name}: {e}")
        return False
        
    def read(self, name: str) -> int:
        """Read pin state (1=High, 0=Low, -1=Error)"""
        pin = self.pins.get(name)
        if pin:
            try:
                return pin.read()
            except Exception as e:
                error(f"GPIO read failed for {name}: {e}")
        return -1
        
    def cleanup(self):
        """Cleanup all pins"""
        for name, pin in self.pins.items():
            try:
                pin.cleanup()
            except Exception as e:
                error(f"GPIO cleanup failed for {name}: {e}")
        self.pins.clear()