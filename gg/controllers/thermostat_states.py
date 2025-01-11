from ..logging.Log import debug
import time

# Define states as constants
STATE_IDLE = "idle"
STATE_HEATING = "heating"
STATE_CYCLE_DELAY = "cycle_delay"
STATE_MIN_RUN = "min_run"
STATE_DISABLED = "disabled"

class ThermostatStateManager:
    def __init__(self, controller):
        self.controller = controller
        self._state = STATE_IDLE
        self._last_state = None
        self._cycle_delay_start = 0
        
    @property
    def state(self):
        return self._state
        
    def can_transition(self, new_state):
        """Check if transition to new state is allowed"""
        if new_state == STATE_HEATING and self._state == STATE_CYCLE_DELAY:
            time_in_delay = time.time() - self._cycle_delay_start
            return time_in_delay >= self.controller._cycle_delay
        return True
        
    async def transition(self, new_state: str):
        if new_state == self._state:  # Don't log if state hasn't changed
            return
            
        if not self.can_transition(new_state):
            return
            
        self._last_state = self._state
        self._state = new_state
        
        # Track cycle delay start time and log state changes
        if new_state == STATE_CYCLE_DELAY:
            self._cycle_delay_start = time.time()
            remaining = int(self.controller._cycle_delay)
            debug(f"Status: Temp={self.controller._current_temp}°F, "
                  f"Setpoint={self.controller.setpoint}°F - "
                  f"Cycle delay in effect ({remaining}s remaining)")
                  
        elif new_state == STATE_HEATING:
            debug(f"*** Temperature {self.controller._current_temp}°F below "
                  f"setpoint {self.controller.setpoint}°F - turning ON ***")
                  
        elif new_state == STATE_IDLE and self._last_state == STATE_HEATING:
            debug(f"*** Temperature {self.controller._current_temp}°F above "
                  f"setpoint {self.controller.setpoint}°F - turning OFF ***")
                  
        elif new_state == STATE_MIN_RUN:
            remaining = int(self.controller._min_run_time - 
                          (time.time() - self.controller._last_on_time))
            debug(f"DEBUG: min_run_time={self.controller._min_run_time}, " +
                  f"last_on_time={self.controller._last_on_time}, " +
                  f"current_time={time.time()}")
            if remaining > 0:
                debug(f"Minimum run time in effect: {remaining}s remaining") 