from .core.Events import EventSystem
from .core.Rules import RulesEngine
from .core.Safety import SafetyMonitor
from .controllers.Base import BaseController
from .controllers.Temperature import TemperatureController
from .controllers.Thermostat import ThermostatController
from .devices.HeaterRelay import HeaterRelay
from .devices.TempSensorADT7410 import TempSensorADT7410
from .config import PinConfig, I2CConfig
from machine import I2C, Pin
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
        
        try:
            # Initialize each subsystem
            if not await self.events.start():
                return False
            if not await self.safety.start():
                return False
            if not await self.rules.start():
                return False
                
            # Subscribe to system events
            self.events.subscribe("controller_error", self._handle_error)
            self.events.subscribe("controller_disabled", self._handle_controller_disabled)
            
            # Temperature events
            self.events.subscribe("temperature_current", self._handle_temperature)
            self.events.subscribe("temperature_changed", self._handle_temperature_change)
            
            # Thermostat events
            self.events.subscribe("heater_on", self._handle_heater_on)
            self.events.subscribe("heater_off", self._handle_heater_off)
            self.events.subscribe("setpoint_changed", self._handle_setpoint_change)
            
            # Safety events
            self.events.subscribe("safety_alert", self._handle_safety_alert)
            self.events.subscribe("safety_cleared", self._handle_safety_cleared)
            
            # Initialize I2C for temperature sensor
            i2c = I2C(0, 
                     scl=Pin(PinConfig.I2C_SCL), 
                     sda=Pin(PinConfig.I2C_SDA),
                     freq=I2CConfig.FREQUENCY)
                     
            # Initialize temperature control
            temp_sensor = TempSensorADT7410(i2c)
            heater_relay = HeaterRelay()
            
            temp_controller = TemperatureController(
                "temperature",
                temp_sensor,
                self.safety,
                self.events
            )
            
            thermostat = ThermostatController(
                "thermostat",
                heater_relay,
                self.safety,
                self.events
            )
            
            # Register controllers
            self.register_device("temperature", temp_controller)
            self.register_device("thermostat", thermostat)
            
            # Initialize all devices
            for name, device in self.devices.items():
                if not await device.initialize():
                    error(f"Failed to initialize {name}")
                    return False
            
            self._monitoring = True
            self.state = SystemState.RUNNING
            return True
            
        except Exception as e:
            critical(f"Initialization failed: {e}")
            self.state = SystemState.ERROR
            return False
        
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