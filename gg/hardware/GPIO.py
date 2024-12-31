from machine import Pin
from ..core.Events import EventSystem

class GPIOController:
    def __init__(self, event_system: EventSystem):
        self.pins = {}
        self.event_system = event_system
        
    def setup_pin(self, name: str, pin_number: int, mode: int, 
                  callback=None, trigger=None):
        """Setup a GPIO pin with optional interrupt"""
        pin = Pin(pin_number, mode)
        if callback and trigger:
            pin.irq(trigger=trigger, handler=callback)
        self.pins[name] = pin
        return pin
        
    def get_pin(self, name: str) -> Pin:
        """Get a pin by name"""
        return self.pins.get(name)
        
    def set_pin(self, name: str, value: int):
        """Set pin value and emit event"""
        if name in self.pins:
            self.pins[name].value(value)
            self.event_system.publish(f"gpio_{name}", value)
            
    def cleanup(self):
        """Cleanup all pins"""
        for pin in self.pins.values():
            pin.value(0)