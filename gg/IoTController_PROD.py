from machine import Pin # type: ignore
import asyncio
from collections import deque
from .core.Events import EventSystem
from .core.Rules import RulesEngine
from .core.Safety import SafetyMonitor
import time
from config import PinConfig
from gg.logging.Log import info, error, critical

# System states
class SystemState:
    """System state enumeration
    
    Defines the possible states of the IoT controller system.
    States control system behavior and safety responses.
    """
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    SHUTDOWN = "shutdown"
    MAINTENANCE = "maintenance"

class IoTController:
    """Main IoT Controller class
    
    Manages the overall system including events, safety monitoring, and rules.
    Coordinates between different subsystems and maintains system state.
    
    Attributes:
        state (SystemState): Current state of the controller
        events (EventSystem): Event management system
        safety (SafetyMonitor): Safety monitoring system
        rules (RuleEngine): Rule processing engine
        error_log (deque): Fixed-size log of system errors
        
    Example:
        >>> controller = IoTController()
        >>> await controller.initialize()
        >>> controller.state
        'ready'
    """
    
    def __init__(self):
        """Initialize the IoT controller
        
        Sets up core systems and initializes to INITIALIZING state.
        Creates event system, rules engine, and error log.
        """
        self.state = SystemState.INITIALIZING
        self.error_log = deque((), 10)
        
        # Initialize systems
        self.events = EventSystem()
        self.rules = RulesEngine(self.events)
        self.safety = SafetyMonitor()

    async def initialize(self):
        """Initialize the controller and all subsystems
        
        Sets up event handlers, safety checks, and rules. Transitions to
        READY state if successful.
        
        Returns:
            bool: True if initialization successful, False otherwise
            
        Example:
            >>> controller = IoTController()
            >>> success = await controller.initialize()
            >>> if success:
            ...     print("System ready")
        """
        info("Initializing...")
        # Subscribe to system events
        self.events.subscribe("system_state", self._handle_state_change)
        self.events.subscribe("system_error", self._handle_error)
        self.events.subscribe("system_command", self._handle_command)
        self.events.subscribe("system_heartbeat", self._handle_heartbeat)
        self.events.subscribe("system_command", self._handle_command)
        
        # Setup safety and rules
        await self._setup_safety_checks()
        await self._setup_default_rules()
        
        # Initialize safety system
        await self._setup_safety_checks()
        
        # Set system to ready state
        self.state = SystemState.READY
        await self.events.publish("system_state", {
            "state": self.state,
            "timestamp": time.time()
        })
        return True
        
    async def _setup_safety_checks(self):
        """Setup safety checks for the system
        
        This method should be overridden by subclasses to add
        specific safety conditions.
        """
        pass
        
    async def _setup_default_rules(self):
        """Setup default system rules
        
        This method should be overridden by subclasses to add
        specific rules for the system.
        """
        pass
        
    async def _handle_state_change(self, event):
        """Handle system state change events
        
        Args:
            event (Event): Event containing new state information
            
        Example:
            >>> await controller._handle_state_change(Event("system_state", {"state": "running"}))
        """
        info(f"System state changed to: {event.data['state']}")
        
    async def _handle_error(self, event):
        """Handle system error events
        
        Args:
            event (Event): Event containing error information
            
        Example:
            >>> await controller._handle_error(Event("system_error", 
            ...     {"message": "Sensor failure", "severity": "high"}))
        """
        error(f"System error: {event.data}")
        self.error_log.append(event.data)
        
    async def _handle_command(self, event):
        """Handle system command events
        
        Args:
            event (Event): Event containing command information
            
        Example:
            >>> await controller._handle_command(Event("system_command", {"command": "shutdown"}))
        """
        if event.data.get('command') == 'shutdown':
            await self.shutdown()
            
    async def _handle_heartbeat(self, event):
        """Handle system heartbeat events
        
        Args:
            event (Event): Heartbeat event data
            
        Example:
            >>> await controller._handle_heartbeat(Event("system_heartbeat", {"timestamp": time.time()}))
        """
        pass
        
    async def shutdown(self):
        """Perform a clean system shutdown
        
        Stops all subsystems and transitions to SHUTDOWN state.
        
        Example:
            >>> await controller.shutdown()
            >>> assert controller.state == SystemState.SHUTDOWN
        """
        info("Shutting down...")
        self.state = SystemState.SHUTDOWN
        await self.events.publish("system_state", {
            "state": self.state,
            "timestamp": time.time()
        })