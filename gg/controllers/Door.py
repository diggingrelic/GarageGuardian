from .base import BaseController
from micropython import const
import time

# Door operation constants
DOOR_TIMEOUT = const(30)     # Max seconds for door operation
FORCE_LIMIT = const(80)      # Motor force limit (percent)
MIN_CYCLE_GAP = const(5)     # Minimum seconds between operations
MAX_DAILY_CYCLES = const(100)  # Maximum door operations per day

class DoorState:
    CLOSED = "closed"
    OPEN = "open"
    OPENING = "opening"
    CLOSING = "closing"
    STOPPED = "stopped"
    ERROR = "error"

class DoorController(BaseController):
    def __init__(self, door_pin, sensor_pin, safety_pin=None, 
                 motion_pin=None, light_pin=None, event_system=None):
        super().__init__('door')
        
        # Hardware setup
        self.door_relay = door_pin
        self.position_sensor = sensor_pin
        self.safety_sensor = safety_pin
        self.motion_sensor = motion_pin
        self.light = light_pin
        self.event_system = event_system
        
        # State tracking
        self.state = DoorState.CLOSED
        self.last_state = DoorState.CLOSED
        self.operation_start = 0
        self.last_operation = 0
        self.cycle_count = 0
        self.last_cycle_reset = time.time()
        self.obstruction_count = 0
        
        # Motion detection
        self.last_motion = 0
        self.light_timeout = 300  # 5 minutes
        
    async def update(self):
        """Update door state and check safety"""
        if not self.enabled:
            return
            
        current_time = time.time()
        
        # Reset daily cycle count
        if current_time - self.last_cycle_reset > 86400:  # 24 hours
            self.cycle_count = 0
            self.last_cycle_reset = current_time
            
        # Check door position
        self._update_position()
        
        # Check for timeout during operation
        if self.state in [DoorState.OPENING, DoorState.CLOSING]:
            if current_time - self.operation_start > DOOR_TIMEOUT:
                await self.handle_timeout()
                
        # Check motion sensor and control light
        if self.motion_sensor and self.light:
            await self._handle_motion()
            
        # Update state if completed movement
        if self.state == DoorState.OPENING and self._is_fully_open():
            await self._complete_operation(DoorState.OPEN)
        elif self.state == DoorState.CLOSING and self._is_fully_closed():
            await self._complete_operation(DoorState.CLOSED)
            
    async def operate_door(self, action):
        """Operate the door"""
        if not self.enabled or not await self._check_safety():
            return False
            
        current_time = time.time()
        
        # Check cycle count
        if self.cycle_count >= MAX_DAILY_CYCLES:
            await self._handle_error("Max daily cycles exceeded")
            return False
            
        # Check minimum time between operations
        if current_time - self.last_operation < MIN_CYCLE_GAP:
            return False
            
        if action == "open" and self.state in [DoorState.CLOSED, DoorState.STOPPED]:
            self.state = DoorState.OPENING
            self.door_relay.value(1)
            self.operation_start = current_time
            self.cycle_count += 1
            await self._publish_state()
            return True
            
        elif action == "close" and self.state in [DoorState.OPEN, DoorState.STOPPED]:
            if await self._check_safety():
                self.state = DoorState.CLOSING
                self.door_relay.value(1)
                self.operation_start = current_time
                self.cycle_count += 1
                await self._publish_state()
                return True
                
        return False
        
    async def stop_door(self):
        """Emergency stop"""
        self.door_relay.value(0)
        self.last_operation = time.time()
        self.state = DoorState.STOPPED
        await self._publish_state()
        
    async def _check_safety(self):
        """Check all safety conditions"""
        if self.safety_sensor and self.safety_sensor.value():
            self.obstruction_count += 1
            await self._publish_safety_event("obstruction_detected")
            return False
            
        return True
        
    def _update_position(self):
        """Update door position from sensor"""
        if self.position_sensor.value():
            self._handle_position_change()
            
    async def _handle_motion(self):
        """Handle motion detection and lighting"""
        if self.motion_sensor.value():
            self.last_motion = time.time()
            if not self.light.value():
                self.light.value(1)
                await self._publish_state("light_on")
        elif self.light.value() and \
             time.time() - self.last_motion > self.light_timeout:
            self.light.value(0)
            await self._publish_state("light_off")
            
    async def handle_timeout(self):
        """Handle operation timeout"""
        await self.stop_door()
        await self._handle_error("Operation timeout")
        
    async def _handle_error(self, error):
        """Handle error conditions"""
        self.state = DoorState.ERROR
        if self.event_system:
            await self.event_system.publish(
                'door_error',
                {
                    'error': error,
                    'state': self.state,
                    'time': time.time()
                }
            )
            
    async def _publish_state(self, event_type='door_state'):
        """Publish state change event"""
        if self.event_system:
            await self.event_system.publish(
                event_type,
                {
                    'state': self.state,
                    'previous': self.last_state,
                    'time': time.time()
                }
            )
            
    async def _complete_operation(self, new_state):
        """Complete a door operation"""
        self.last_state = self.state
        self.state = new_state
        self.door_relay.value(0)
        self.last_operation = time.time()
        await self._publish_state()
        
    def _is_fully_open(self):
        """Check if door is fully open"""
        return self.position_sensor.value() == 1
        
    def _is_fully_closed(self):
        """Check if door is fully closed"""
        return self.position_sensor.value() == 0
        
    def get_state(self):
        """Get current state"""
        state = super().get_state()
        state.update({
            'door_state': self.state,
            'cycles_today': self.cycle_count,
            'last_operation': self.last_operation,
            'obstructions': self.obstruction_count,
            'light_on': self.light.value() if self.light else None,
            'safety_sensor': self.safety_sensor.value() if self.safety_sensor else None
        })
        return state