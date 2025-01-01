from machine import Pin # type: ignore
import asyncio
from collections import deque
from .core.Events import EventSystem
import time
import gc
from config import PinConfig
from .logging.Log import log

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
        
        # Initialize event system
        self.events = EventSystem()
        
    async def initialize(self):
        print("Initializing...")
        # Subscribe to system events
        self.events.subscribe("system_state", self._handle_state_change)
        self.events.subscribe("system_error", self._handle_error)
        self.events.subscribe("system_heartbeat", self._handle_heartbeat)
        self.events.subscribe("system_command", self._handle_command)
        
        # Set system to ready state
        self.state = SystemState.READY
        await self.events.publish("system_state", {
            "state": self.state,
            "timestamp": time.time()
        })
        
        return True

    async def run(self):
        print("Running...")
        self.state = SystemState.RUNNING
        
        # Publish state change
        await self.events.publish("system_state", {
            "state": self.state,
            "timestamp": time.time()
        })
        
        while self.state == SystemState.RUNNING:
            self.led.toggle()
            
            # Publish heartbeat event
            await self.events.publish("system_heartbeat", {
                "led_state": self.led.value(),
                "uptime": time.time(),
                "memory_free": gc.mem_free() if hasattr(gc, 'mem_free') else 0
            })
            await asyncio.sleep(1)

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
        print(f"System state changed: {event.data['state']}")
        # Add any state transition logic here

    async def _handle_error(self, event):
        """Handle system error events"""
        print(f"System error: {event.data['message']} (Level: {event.data['level']})")

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
        print("Shutting down...")
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
