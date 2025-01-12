from .core.Events import EventSystem
from .core.Rules import RulesEngine
from .core.Safety import SafetyMonitor
from .controllers.Base import BaseController
from .logging.Log import info, error, critical, debug
import time
import asyncio
from config import SystemConfig

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
    
    def __init__(self, event_system=None, safety_monitor=None):
        self.events = event_system or EventSystem()
        self.safety = safety_monitor or SafetyMonitor()
        self.devices = {}
        self.rules = RulesEngine(self.events)
        self.state = SystemState.INITIALIZING
        self._monitoring = False  # Initialize monitoring flag here
        
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
        
    async def initialize(self, device_factory=None):
        """Initialize the IoT controller system"""
        info("Starting IoT controller")
        self.state = SystemState.INITIALIZING
        
        try:
            # Initialize core systems
            if not await self.events.start():
                return False
            if not await self.safety.start():
                return False
            if not await self.rules.start():
                return False

            if device_factory:
                # Let factory create and register devices
                if not await device_factory.create_devices(self):
                    return False
                    
            # Start monitoring loop for temperature
            temp_controller = self.get_device("temperature")
            if temp_controller:
                self._monitoring = True
                asyncio.create_task(self._monitor_temperature(temp_controller))
                
            self.state = SystemState.RUNNING
            return True
            
        except Exception as e:
            critical(f"Initialization failed: {e}")
            self.state = SystemState.ERROR
            return False
            
    async def _monitor_temperature(self, temp_controller):
        """Background task to monitor temperature"""
        while self.state == SystemState.RUNNING:
            await temp_controller.monitor()
            await asyncio.sleep_ms(100)  # Small delay between checks
        
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
        
    async def _handle_error(self, event):
        """Handle error events from controllers"""
        error(f"Controller {event['controller']}: {event['error']}")
        
    async def _handle_controller_disabled(self, event):
        """Handle controller shutdown events"""
        info(f"Controller {event['name']} disabled at {event['timestamp']}")
        
    async def _handle_temperature(self, event):
        """Handle current temperature events"""
        info(f"Current temperature: {event['temp']}°F")
        
    async def _handle_temperature_change(self, event):
        """Handle temperature change events"""
        info(f"Temperature changed from {event['previous']}°F to {event['temp']}°F")
        
    async def _handle_heater_on(self, event):
        """Handle heater activation events"""
        info(f"Heater activated at {event['temp']}°F (setpoint: {event['setpoint']}°F)")
        
    async def _handle_heater_off(self, event):
        """Handle heater deactivation events"""
        info(f"Heater deactivated at {event['temp']}°F (setpoint: {event['setpoint']}°F)")
        
    async def _handle_setpoint_change(self, event):
        """Handle thermostat setpoint changes"""
        info(f"Thermostat setpoint changed to {event['temp']}°F")
        
    async def _handle_safety_alert(self, event):
        """Handle safety condition alerts"""
        critical(f"Safety alert: {event['condition']} - {event['message']}")
        
    async def _handle_safety_cleared(self, event):
        """Handle safety condition clearing"""
        info(f"Safety condition cleared: {event['condition']}")
        
    async def update_system_setting(self, category, setting, value):
        """Update system setting and notify all relevant controllers"""
        config = SystemConfig.get_instance()
        success, old_value = config.update_setting(category, setting, value)
        
        if success:
            if category == 'TEMP_SETTINGS':
                thermostat = self.get_device('thermostat')
                if thermostat:
                    await thermostat.handle_config_update(setting, value)
            
            await self.publish_event("system_setting_changed", {
                "category": category,
                "setting": setting,
                "old_value": old_value,
                "new_value": value,
                "timestamp": time.time()
            })
            return True
        return False
        
    async def publish_event(self, event_type, data):
        """Publish an event to all subscribers"""
        if hasattr(self, 'events') and self.events:
            await self.events.publish(event_type, data)
        else:
            debug(f"Event system not initialized: {event_type} - {data}")
        
    async def start_timed_heat(self, hours):
        """Start timed heating operation"""
        seconds = int(hours * 3600)
        thermostat = self.get_device('thermostat')
        
        if thermostat:
            # Start heating now
            await self.events.publish("thermostat_timer_start", {
                "action": "enable",
                "timestamp": int(time.time())
            })
            
            # Calculate end time
            self.timer_end_time = int(time.time() + seconds)
            
            # Schedule regular checks
            asyncio.create_task(self._check_timer())
            return True
        return False
        
    async def _check_timer(self):
        """Regularly check if the timer has expired"""
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            if time.time() >= self.timer_end_time:
                # Timer expired
                await self.events.publish("thermostat_timer_end", {
                    "action": "disable",
                    "timestamp": int(time.time())
                })
                break