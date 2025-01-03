from machine import Pin # type: ignore
import asyncio
from collections import deque
from .core.Events import EventSystem
from .core.Rules import RulesEngine
from .core.Safety import SafetyMonitor
import time
from config import PinConfig
from gg.logging.Log import info, error, critical

class SystemState:
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class IoTController:
    def __init__(self):
        self.led = Pin(PinConfig.STATUS_LED, Pin.OUT)
        self.state = SystemState.INITIALIZING
        self.error_log = deque((), 10)
        
        # Initialize systems
        self.events = EventSystem()
        self.rules = RulesEngine(self.events)
        self.safety = SafetyMonitor(self.events)  # Add Safety Monitor
        
    async def initialize(self):
        info("Initializing...")
        # Subscribe to system events
        self.events.subscribe("system_state", self._handle_state_change)
        self.events.subscribe("system_error", self._handle_error)
        self.events.subscribe("system_command", self._handle_command)
        self.events.subscribe("system_heartbeat", self._handle_heartbeat)
        self.events.subscribe("system_command", self._handle_command)
        
        # Initialize rules engine
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
        """Setup safety checks - override in subclasses"""
        pass  # Safety checks will be added by subclassing
        
    async def run(self):
        """Main run loop"""
        if self.state == SystemState.RUNNING:
            # Check safety conditions first
            if not await self.safety.check_safety():
                error("Safety check failed")
                await self._handle_safety_violation()
                return
                
            # If safe, process rules
            await self.rules.process_rules()
                
    async def _handle_safety_violation(self):
        """Handle safety violations"""
        critical_conditions = self.safety.get_critical_conditions()
        if critical_conditions:
            critical(f"Critical safety violation: {critical_conditions}")
            await self.safety.emergency_stop()
            self.state = SystemState.ERROR

    async def _setup_default_rules(self):
        """Setup default system rules - override in subclasses"""
        pass  # Default rules can be added by subclassing

    def _log_error(self, error, level="ERROR"):
        """Log an error and publish error event"""
        error_data = {
            "message": str(error),
            "level": level,
            "timestamp": time.time()
        }
        self.error_log.append(error_data)
        # Publish error event
        asyncio.create_task(self.events.publish("system_error", error_data))

    async def _handle_state_change(self, event):
        """Handle system state change events"""
        info(f"System state changed: {event.data['state']}")
        # Add any state transition logic here

    async def _handle_error(self, event):
        """Handle system error events"""
        error(f"System error: {event.data['message']} (Level: {event.data['level']})")

    async def _handle_heartbeat(self, event):
        """Handle system heartbeat events"""
        # We can add system health checks here
        pass

    async def _handle_command(self, event):
        """Handle system command events"""
        if 'command' in event.data:
            command = event.data['command']
            if command == 'shutdown':
                await self.shutdown()
            elif command == 'restart':
                await self.restart()
            # Add more commands as needed

    async def shutdown(self):
        """Perform a clean shutdown"""
        info("Shutting down...")
        self.state = SystemState.SHUTDOWN
        await self.events.publish("system_state", {
            "state": self.state,
            "timestamp": time.time()
        })
        self.led.off()

    async def restart(self):
        """Restart the controller"""
        await self.shutdown()
        self.state = SystemState.INITIALIZING
        await self.initialize()