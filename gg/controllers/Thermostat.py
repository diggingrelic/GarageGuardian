from .Base import BaseController
import time
from micropython import const #type: ignore
from config import SystemConfig
# Thermostat constants
MIN_CYCLE_TIME = const(300)  # 5 minutes minimum run time
MAX_CYCLE_TIME = const(1800)  # 30 minutes maximum run time
TEMP_THRESHOLD = const(0.5)   # Temperature variance threshold
MAX_DAILY_CYCLES = const(48)  # Maximum heating cycles per day

class ThermostatMode:
    OFF = "off"
    HEAT = "heat"
    AUTO = "auto"
    AWAY = "away"

class ThermostatController(BaseController):
    def __init__(self, heater_pin, sensor_manager, event_system=None):
        super().__init__('thermostat')
        
        # Hardware interfaces
        self.heater = heater_pin
        self.sensor_manager = sensor_manager
        self.event_system = event_system
        
        # Temperature settings
        self.target_temp = 20.0
        self.temp_tolerance = 0.5
        self.current_temp = None
        self.mode = ThermostatMode.OFF
        
        # Timing controls
        self.min_run_time = MIN_CYCLE_TIME
        self.cycle_delay = 180  # 3 minutes between cycles
        self.last_run_time = 0
        self.run_start_time = 0
        self.cycle_count = 0
        self.last_cycle_reset = time.time()
        
        # Temperature history
        self.temp_history = []
        self.max_history = 100
        
        # Schedule
        self.schedule = {}
        self.schedule_enabled = False
        
    async def update(self):
        """Update thermostat state"""
        if not self.enabled:
            await self.stop_heating()
            return
            
        # Read current temperature
        temp = await self.sensor_manager.read_sensor('temperature')
        if temp is not None:
            self.current_temp = temp
            self.temp_history.append((time.time(), temp))
            if len(self.temp_history) > self.max_history:
                self.temp_history.pop(0)
        
        # Check schedule
        if self.schedule_enabled:
            await self._check_schedule()
        
        # Update heating based on mode
        if self.mode != ThermostatMode.OFF:
            await self._update_heating()
            
    async def _update_heating(self):
        """Update heating state based on temperature"""
        current_time = time.time()
        
        # Check cycle count
        if current_time - self.last_cycle_reset > 86400:  # 24 hours
            self.cycle_count = 0
            self.last_cycle_reset = current_time
            
        if self.cycle_count >= MAX_DAILY_CYCLES:
            await self.stop_heating()
            return
            
        # Check if heating is needed
        if self.current_temp < (self.target_temp - self.temp_tolerance):
            if not self.heater.value():  # If heater is off
                # Check cycle delay
                if current_time - self.last_run_time > self.cycle_delay:
                    await self.start_heating()
        elif self.current_temp > (self.target_temp + self.temp_tolerance):
            if self.heater.value():  # If heater is on
                # Check minimum run time
                if current_time - self.run_start_time > self.min_run_time:
                    await self.stop_heating()
                    
    async def start_heating(self):
        """Start the heating cycle"""
        if not self.enabled:
            return
            
        self.heater.value(1)
        self.run_start_time = time.time()
        self.cycle_count += 1
        
        if self.event_system:
            await self.event_system.publish(
                'heater_state',
                {
                    'state': 'on',
                    'temp': self.current_temp,
                    'target': self.target_temp
                }
            )
            
    async def stop_heating(self):
        """Stop the heating cycle"""
        self.heater.value(0)
        self.last_run_time = time.time()
        
        if self.event_system:
            await self.event_system.publish(
                'heater_state',
                {
                    'state': 'off',
                    'temp': self.current_temp,
                    'target': self.target_temp
                }
            )
            
    async def set_temperature(self, temp):
        """Set target temperature"""
        if SystemConfig.MIN_TEMP <= temp <= SystemConfig.MAX_TEMP:
            self.target_temp = temp
            if self.event_system:
                await self.event_system.publish(
                    'temp_set',
                    {
                        'target': temp,
                        'current': self.current_temp
                    }
                )
            return True
        return False
        
    async def set_mode(self, mode):
        """Set thermostat mode"""
        if mode in [ThermostatMode.OFF, ThermostatMode.HEAT, 
                   ThermostatMode.AUTO, ThermostatMode.AWAY]:
            self.mode = mode
            if mode == ThermostatMode.OFF:
                await self.stop_heating()
            elif mode == ThermostatMode.AWAY:
                self.previous_target = self.target_temp
                self.target_temp = self.away_temp
            return True
        return False
        
    def add_schedule(self, time_str, temp):
        """Add a scheduled temperature change"""
        self.schedule[time_str] = temp
        
    async def _check_schedule(self):
        """Check and apply schedule"""
        if not self.schedule_enabled:
            return
            
        current_time = time.localtime()
        time_str = f"{current_time[3]:02d}:{current_time[4]:02d}"
        
        if time_str in self.schedule:
            await self.set_temperature(self.schedule[time_str])
            
    async def emergency_shutdown(self):
        """Emergency shutdown procedure"""
        await self.stop_heating()
        self.enabled = False
        self.mode = ThermostatMode.OFF
        
        if self.event_system:
            await self.event_system.publish(
                'thermostat_emergency',
                {
                    'temp': self.current_temp,
                    'time': time.time()
                }
            )
            
    def get_state(self):
        """Get current state"""
        state = super().get_state()
        state.update({
            'current_temp': self.current_temp,
            'target_temp': self.target_temp,
            'mode': self.mode,
            'heating': bool(self.heater.value()),
            'cycle_count': self.cycle_count,
            'schedule_enabled': self.schedule_enabled,
            'last_cycle': self.last_run_time
        })
        return state