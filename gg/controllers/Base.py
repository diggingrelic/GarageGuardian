import time
import asyncio
from micropython import const

# Base controller constants
WATCHDOG_TIMEOUT = const(30)  # seconds
MAX_ERROR_COUNT = const(5)    # max errors before disable
ERROR_RESET_TIME = const(3600)  # 1 hour to reset error count

class ControllerState:
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"

class BaseController:
    def __init__(self, name):
        # Basic properties
        self.name = name
        self.state = ControllerState.INITIALIZING
        self.enabled = True
        
        # Error tracking
        self.error_count = 0
        self.last_error = None
        self.last_error_time = 0
        
        # Activity monitoring
        self.last_update = 0
        self.update_count = 0
        self.watchdog_time = 0
        
        # Configuration
        self.config = {}
        
        # Event system (set by IoTController)
        self.event_system = None
        
    async def update(self):
        """
        Main update loop - must be implemented by child classes
        """
        raise NotImplementedError
        
    async def process_command(self, action, params=None):
        """
        Process a command sent to this controller
        """
        try:
            self.last_update = time.time()
            self.update_count += 1
            
            if not self.enabled:
                raise Exception("Controller is disabled")
                
            # Implement command processing in child class
            result = await self._process_command(action, params or {})
            
            # Reset error count on successful command
            await self._reset_errors()
            
            return result
            
        except Exception as e:
            await self._handle_error(f"Command error: {e}")
            return False
            
    async def _process_command(self, action, params):
        """
        To be implemented by child classes
        """
        raise NotImplementedError
        
    async def enable(self):
        """Enable the controller"""
        self.enabled = True
        self.state = ControllerState.READY
        await self._publish_state()
        
    async def disable(self):
        """Disable the controller"""
        self.enabled = False
        self.state = ControllerState.DISABLED
        await self._publish_state()
        
    async def safe_shutdown(self):
        """
        Perform safe shutdown - can be extended by child classes
        """
        self.enabled = False
        self.state = ControllerState.DISABLED
        await self._publish_state()
        
    async def _handle_error(self, error):
        """Handle error conditions"""
        self.last_error = error
        self.last_error_time = time.time()
        self.error_count += 1
        
        if self.error_count >= MAX_ERROR_COUNT:
            await self.disable()
            
        if self.event_system:
            await self.event_system.publish(
                f'{self.name}_error',
                {
                    'error': error,
                    'count': self.error_count,
                    'time': self.last_error_time
                }
            )
            
    async def _reset_errors(self):
        """Reset error count if enough time has passed"""
        if (time.time() - self.last_error_time) > ERROR_RESET_TIME:
            self.error_count = 0
            
    async def _publish_state(self):
        """Publish state change event"""
        if self.event_system:
            await self.event_system.publish(
                f'{self.name}_state',
                self.get_state()
            )
            
    def set_config(self, config):
        """Update controller configuration"""
        self.config.update(config)
        
    def get_config(self):
        """Get current configuration"""
        return self.config.copy()
        
    def get_state(self):
        """
        Get controller state - can be extended by child classes
        """
        return {
            'name': self.name,
            'state': self.state,
            'enabled': self.enabled,
            'last_update': self.last_update,
            'update_count': self.update_count,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_error_time': self.last_error_time
        }
        
    def check_watchdog(self):
        """Check if controller is responding"""
        current_time = time.time()
        if current_time - self.last_update > WATCHDOG_TIMEOUT:
            return False
        return True
        
    async def maintenance_mode(self, enabled=True):
        """Enter or exit maintenance mode"""
        if enabled:
            self.state = ControllerState.MAINTENANCE
            self.enabled = False
        else:
            self.state = ControllerState.READY
            self.enabled = True
        await self._publish_state()