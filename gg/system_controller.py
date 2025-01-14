from .core.Events import EventSystem
from .core.Rules import RulesEngine
from .core.Safety import SafetyMonitor
from .controllers.Base import BaseController
from .services.Base import BaseService
from .logging.Log import info, error, critical, debug
import time
import asyncio
from config import SystemConfig
from gg.logging.cowbell_logger import SimpleLogger
import os

class SystemState:
    """System state enumeration"""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class SystemController:
    """Main controller for IoT system
    
    Manages device controllers, coordinates monitoring,
    and integrates with core systems (Events, Rules, Safety).
    
    Example usage:
        controller = SystemController()
        door = DoorController(RealDoor(sensor_pin=16, lock_pin=17), controller.events)
        controller.register_device("main_door", door)
        await controller.start()
    """
    
    def __init__(self, event_system=None, safety_monitor=None, settings_manager=None):
        self.events = event_system or EventSystem()
        self.safety = safety_monitor or SafetyMonitor()
        self.settings = settings_manager
        self.devices = {}
        self.services = {}
        self.rules = RulesEngine(self.events)
        self.state = SystemState.INITIALIZING
        self._monitoring = False
        self.logger = SimpleLogger.get_instance()
        self.timer_end_time = None
        
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

    def register_service(self, name: str, service: BaseService) -> bool:
        """Register a service
        
        Args:
            name (str): Unique name for the service
            service (BaseService): Service instance
            
        Returns:
            bool: True if registration successful
        """
        if name in self.services:
            error(f"Service {name} already registered")
            return False
            
        self.services[name] = service
        info(f"Service {name} registered")
        return True
        
    async def initialize(self, device_factory=None):
        """Initialize controller and devices"""
        try:
            info("Starting IoT controller")
            self.state = SystemState.INITIALIZING
            
            # Initialize core systems
            if not await self.events.start():
                return False
            if not await self.safety.start():
                return False
            if not await self.rules.start():
                return False

            # Restore settings from SD Card
            await self.settings.restore_all_settings()

            # Initialize devices
            if device_factory:
                # Let factory create and register devices
                if not await device_factory.create_devices(self):
                    return False
                    
            # Start monitoring loop for temperature using BMP390 service
            bmp390 = self.get_service("bmp390")
            if bmp390:
                self._monitoring = True
                asyncio.create_task(self._monitor_temperature(bmp390))
            else:
                error("BMP390 service not found")
                return False

            # Check for existing timer
            try:
                os.stat('/sd/timer.json')
                # File exists, load it
                timer_state = self.logger.load_state(state_file="timer.json")
                if timer_state:
                    current_time = time.time()
                    timer_end = timer_state.get('timer_end')
                    
                    if timer_end and timer_end > current_time:
                        # Timer still valid, resume it
                        remaining_mins = (timer_end - current_time) / 60
                        debug(f"Restoring timer with {remaining_mins:.1f} minutes remaining")
                        self.timer_end_time = timer_end
                        config = SystemConfig.get_instance()
                        config.update_setting('TIMER_SETTINGS', 'END_TIME', timer_end)
                        asyncio.create_task(self._check_timer())
                    else:
                        # Timer expired, delete it
                        debug("Timer expired during shutdown, deleting timer state")
                        self.logger.delete_state(state_file="timer.json")
            except OSError:
                # File doesn't exist, that's fine
                pass
            
            self.state = SystemState.RUNNING
            
            # Initialize time sync tracking
            self.last_time_sync = time.time()
            
            return True
        except Exception as e:
            critical(f"Initialization failed: {e}")
            self.state = SystemState.ERROR
            return False
        
    async def _monitor_temperature(self, bmp390):
        """Background task to monitor temperature"""
        debug("Starting temperature monitoring loop")
        while self.state == SystemState.RUNNING:
            temp = bmp390.get_fahrenheit()
            if temp is not None:
                await self.events.publish("temperature_current", {
                    "temp": temp,
                    "timestamp": time.time()
                })
            else:
                error("Failed to read temperature from BMP390")
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
            
        # Check if time sync needed
        await self._check_time_sync()
        
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
    
    def get_service(self, name: str):
        """Get a registered service by name"""
        return self.services.get(name)
        
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
        
    async def _handle_safety_alert(self, event):
        """Handle safety condition alerts"""
        critical(f"Safety alert: {event['condition']} - {event['message']}")
        
    async def _handle_safety_cleared(self, event):
        """Handle safety condition clearing"""
        info(f"Safety condition cleared: {event['condition']}")
        
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
            # Calculate end time
            self.timer_end_time = int(time.time() + seconds)
            
            # Update config for runtime settings
            config = SystemConfig.get_instance()
            success, _ = config.update_setting('TIMER_SETTINGS', 'END_TIME', self.timer_end_time)
            
            if success:
                # Save to timer.json for persistence across reboots
                state = {
                    'timer_end': self.timer_end_time,
                    'duration_hours': hours,
                    'timestamp': time.time()
                }
                self.logger.save_state(state, state_file="timer.json")
            
            # Start heating now
            await self.events.publish("thermostat_timer_start", {
                "action": "enable",
                "timestamp": int(time.time())
            })
            
            # Schedule regular checks
            asyncio.create_task(self._check_timer())
            return True
        return False
        
    async def _check_timer(self):
        """Regularly check if the timer has expired"""
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            if time.time() >= self.timer_end_time:
                # Timer expired, delete the file
                self.logger.delete_state(state_file="timer.json")
                # Send the event
                await self.events.publish("thermostat_timer_end", {
                    "action": "disable",
                    "timestamp": int(time.time())
                })
                break
        
    async def _check_time_sync(self):
        """Check if it's time to sync and send event if needed"""
        SYNC_INTERVAL = 300  # 1 hour in seconds
        current_time = time.time()
        if current_time - self.last_time_sync >= SYNC_INTERVAL:
            # Send sync event using events.publish instead of event_queue
            await self.events.publish("sync_time", None)
            self.last_time_sync = current_time

    async def handle_sync_time(self, _):
        """Handle time sync event"""
        try:
            self.logger.sync_system_time()
            debug("System time synced with RTC")
        except Exception as e:
            error(f"Time sync error: {e}")