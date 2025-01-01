from .Base import BaseController
from micropython import const
import time

# Power management constants
MAX_TOTAL_LOAD = const(1500)  # Watts
OVERLOAD_THRESHOLD = const(0.9)  # 90% of max load
MIN_TOGGLE_INTERVAL = const(1)  # Minimum seconds between toggles
POWER_SAMPLING_RATE = const(5)  # Seconds between power readings

class PowerState:
    ON = "on"
    OFF = "off"
    OVERLOAD = "overload"
    ERROR = "error"

class PowerController(BaseController):
    def __init__(self, outlet_pins, current_sensor=None, event_system=None):
        super().__init__('power')
        
        # Hardware setup
        self.outlets = {}  # Dictionary of outlet pins
        self.setup_outlets(outlet_pins)
        self.current_sensor = current_sensor
        self.event_system = event_system
        
        # State tracking
        self.states = {}  # Outlet states
        self.power_readings = {}  # Power consumption per outlet
        self.last_toggle = {}  # Last toggle time per outlet
        self.total_power = 0
        self.last_reading = 0
        
        # Power monitoring history
        self.power_history = []
        self.max_history = 100
        
    def setup_outlets(self, outlet_pins):
        """Initialize outlets"""
        for name, pin in outlet_pins.items():
            self.outlets[name] = pin
            self.states[name] = PowerState.OFF
            self.power_readings[name] = 0
            self.last_toggle[name] = 0
            pin.value(0)  # Ensure outlets start OFF
            
    async def update(self):
        """Update power controller state"""
        if not self.enabled:
            return
            
        current_time = time.time()
        
        # Update power readings periodically
        if current_time - self.last_reading >= POWER_SAMPLING_RATE:
            await self._update_power_readings()
            
        # Check for overload conditions
        await self._check_power_limits()
        
    async def control_outlet(self, outlet_name, state):
        """Control individual outlet"""
        if not self.enabled or outlet_name not in self.outlets:
            return False
            
        current_time = time.time()
        
        # Check toggle rate limit
        if current_time - self.last_toggle.get(outlet_name, 0) < MIN_TOGGLE_INTERVAL:
            return False
            
        try:
            # Set outlet state
            self.outlets[outlet_name].value(1 if state else 0)
            self.states[outlet_name] = PowerState.ON if state else PowerState.OFF
            self.last_toggle[outlet_name] = current_time
            
            # Publish state change
            if self.event_system:
                await self.event_system.publish(
                    'outlet_state',
                    {
                        'outlet': outlet_name,
                        'state': self.states[outlet_name],
                        'time': current_time
                    }
                )
            return True
            
        except Exception as e:
            await self._handle_error(f"Outlet control error: {e}")
            return False
            
    async def _update_power_readings(self):
        """Update power consumption readings"""
        if self.current_sensor:
            try:
                # Read total power
                self.total_power = self._read_power()
                self.last_reading = time.time()
                
                # Store in history
                self.power_history.append((self.last_reading, self.total_power))
                if len(self.power_history) > self.max_history:
                    self.power_history.pop(0)
                    
                # Publish power update
                if self.event_system:
                    await self.event_system.publish(
                        'power_update',
                        {
                            'total_power': self.total_power,
                            'time': self.last_reading
                        }
                    )
                    
            except Exception as e:
                await self._handle_error(f"Power reading error: {e}")
                
    def _read_power(self):
        """Read power from current sensor"""
        if self.current_sensor:
            # Convert ADC reading to power
            reading = self.current_sensor.read_u16()
            # This conversion would need to be calibrated for your specific sensor
            return reading * 0.1  # Example conversion
        return 0
        
    async def _check_power_limits(self):
        """Check for power limit violations"""
        if self.total_power > MAX_TOTAL_LOAD * OVERLOAD_THRESHOLD:
            await self._handle_overload()
            
    async def _handle_overload(self):
        """Handle power overload condition"""
        # Disable non-critical outlets
        for outlet_name in self.outlets:
            if self._is_non_critical(outlet_name):
                await self.control_outlet(outlet_name, False)
                
        if self.event_system:
            await self.event_system.publish(
                'power_overload',
                {
                    'total_power': self.total_power,
                    'time': time.time()
                }
            )
            
    async def _handle_error(self, error):
        """Handle error conditions"""
        if self.event_system:
            await self.event_system.publish(
                'power_error',
                {
                    'error': error,
                    'time': time.time()
                }
            )
            
    def _is_non_critical(self, outlet_name):
        """Determine if outlet is non-critical"""
        # Define your critical outlets logic here
        critical_outlets = ['outlet_1']  # Example
        return outlet_name not in critical_outlets
        
    async def safe_shutdown(self):
        """Safe shutdown procedure"""
        # Turn off all non-critical outlets
        for outlet_name in self.outlets:
            if self._is_non_critical(outlet_name):
                await self.control_outlet(outlet_name, False)
        await super().safe_shutdown()
        
    def get_state(self):
        """Get current state"""
        state = super().get_state()
        state.update({
            'outlets': self.states,
            'total_power': self.total_power,
            'last_reading': self.last_reading,
            'power_readings': self.power_readings
        })
        return state