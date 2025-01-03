from .Base import BaseController
from ..core.Safety import SafetySeverity
from ..logging.Log import error

class DoorController(BaseController):
    def __init__(self, door_hardware, safety_monitor=None, event_system=None):
        super().__init__("door", door_hardware, safety_monitor, event_system)
        
    def _setup_safety_conditions(self):
        """Setup door-specific safety conditions"""
        self.safety.add_condition(
            name="door_obstruction",
            check_func=self._check_obstruction,
            severity=SafetySeverity.HIGH
        )
            
    async def open_door(self):
        if self.hardware.is_fully_open():
            return True
            
        if self.hardware.is_obstructed():
            error("Cannot open door: obstruction detected")
            return False
            
        await self.hardware.open()
        return True
        
    async def close_door(self):
        if self.hardware.is_fully_closed():
            return True
            
        if self.hardware.is_obstructed():
            error("Cannot close door: obstruction detected")
            return False
            
        await self.hardware.close()
        return True
        
    def _check_obstruction(self):
        return not self.hardware.is_obstructed()