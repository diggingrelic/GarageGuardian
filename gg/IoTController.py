from .core.Events import EventSystem
from .core.Rules import RulesEngine
from .core.Safety import SafetyMonitor
from .controllers.Base import BaseController
from .logging.Log import info, error, critical
import asyncio
import time

class SystemState:
    """System state enumeration"""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class IoTController:
    """Main controller for IoT system
    
    Manages device controllers, coordinates monitoring,
    and integrates with core systems (Events, Rules, Safety).
    
    Example usage:
        controller = IoTController()
        door = DoorController(RealDoor(sensor_pin=16, lock_pin=17), controller.events)
        controller.register_device("main_door", door)
        await controller.start()
    """
    
    def __init__(self):
        self.events = EventSystem()
        self.rules = RulesEngine(self.events)
        self.safety = SafetyMonitor()
        self.devices = {}  # type: dict[str, BaseController]
        self.state = SystemState.INITIALIZING
        self._monitoring = False
        
    def register_device(self, name: str, device: BaseController) -> bool:
        """Register a device controller
        
        Args:
            name (str): Unique name for the device
            device (BaseController): Device controller instance
            
        Returns:
            bool: True if registration successful
        """
        if name in self.devices:
            error(f"Device {name} already registered")
            return False
            
        self.devices[name] = device
        info(f"Device {name} registered")
        return True
        
    async def initialize(self):
        """Initialize the IoT controller system"""
        info("Starting IoT controller")
        self.state = SystemState.INITIALIZING
        
        # Initialize each subsystem
        if not await self.events.start():
            return False
        if not await self.safety.start():
            return False
        if not await self.rules.start():
            return False
            
        self._monitoring = True
        self.state = SystemState.RUNNING
        return True
        
    async def run(self):
        """Run one monitoring cycle"""
        if self._monitoring:
            try:
                await self._monitor_cycle()
            except Exception as e:
                error(f"Monitoring error: {e}")
                self.state = SystemState.ERROR
                
    async def _monitor_cycle(self):
        """Run one monitoring cycle
        
        Checks all devices, evaluates rules, and verifies safety.
        """
        # Monitor all devices
        for name, device in self.devices.items():
            try:
                await device.monitor()
            except Exception as e:
                error(f"Device {name} monitoring failed: {e}")
                
        # Evaluate rules
        await self.rules.evaluate_all()
        
        # Check safety conditions
        if not await self.safety.check_safety():
            critical("Safety check failed")
            self.state = SystemState.ERROR
            
    async def _handle_heartbeat(self, event):
        """Handle system heartbeat events
        
        Updates system state and verifies all subsystems.
        """
        if self.state == SystemState.RUNNING:
            # Verify all devices are working
            all_working = True
            for name, device in self.devices.items():
                if not device.device.is_working():
                    error(f"Device {name} not working")
                    all_working = False
                    
            if not all_working:
                self.state = SystemState.ERROR
                
    async def safe_shutdown(self):
        """Perform a clean system shutdown"""
        info("Shutting down IoT controller")
        self._monitoring = False
        self.state = SystemState.SHUTDOWN
        
        # Publish shutdown event
        await self.events.publish("system_state", {
            "state": self.state,
            "timestamp": time.time()
        })
        
        # Stop subsystems
        await self.safety.stop()
        await self.events.stop()
        
    def get_device(self, name: str) -> BaseController:
        """Get a registered device controller by name"""
        return self.devices.get(name)