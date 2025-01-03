import asyncio # noqa: F401
from micropython import const # type: ignore

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
    """Base controller class with common functionality"""
    
    def __init__(self, name: str, hardware=None, safety_monitor=None, event_system=None):
        self.name = name
        self.hardware = hardware
        self.safety = safety_monitor
        self.events = event_system
        self.enabled = True
        
    async def initialize(self):
        """Initialize the controller"""
        if self.safety:
            self._setup_safety_conditions()
        if self.events:
            self._setup_event_handlers()
        return True
        
    def _setup_safety_conditions(self):
        """Setup safety conditions - override in subclasses"""
        pass
        
    def _setup_event_handlers(self):
        """Setup event handlers - override in subclasses"""
        pass
        
    async def update(self):
        """Update controller state - override in subclasses"""
        pass
        
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self.hardware, 'cleanup'):
            self.hardware.cleanup()