from enum import Enum
from ..logging.Log import debug
import time

class ThermostatState(Enum):
    IDLE = "idle"
    HEATING = "heating"
    CYCLE_DELAY = "cycle_delay"
    MIN_RUN = "min_run"
    DISABLED = "disabled"

class ThermostatStateManager:
    def __init__(self, controller):
        self.controller = controller
        self._state = ThermostatState.IDLE
        self._last_state = None
        
    @property
    def state(self):
        return self._state
        
    async def transition(self, new_state: ThermostatState):
        if new_state == self._state:
            return
            
        self._last_state = self._state
        self._state = new_state
        
        # Log state transitions with relevant data
        if new_state == ThermostatState.CYCLE_DELAY:
            remaining = int(self.controller._cycle_delay - 
                          (time.time() - self.controller._last_off_time))
            debug(f"Status: Temp={self.controller._current_temp}°F, "
                  f"Setpoint={self.controller.setpoint}°F - "
                  f"Cycle delay in effect ({remaining}s remaining)")
                  
        elif new_state == ThermostatState.HEATING:
            debug(f"*** Temperature {self.controller._current_temp}°F below "
                  f"setpoint {self.controller.setpoint}°F - turning ON ***")
                  
        elif new_state == ThermostatState.IDLE:
            if self._last_state == ThermostatState.HEATING:
                debug(f"*** Temperature {self.controller._current_temp}°F above "
                      f"setpoint {self.controller.setpoint}°F - turning OFF ***") 