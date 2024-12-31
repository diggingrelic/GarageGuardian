from machine import Pin, I2C
import time
import json
import asyncio
from collections import deque
from micropython import const

# Import our components
from .core.Events import EventSystem
from .core.Rules import RulesEngine, RulePriority
from .core.Safety import SafetyMonitor, SafetySeverity
from .core.Comms import CommHandler, MessageType

from .hardware.GPIO import GPIOController
from .hardware.Sensors import SensorManager

from .controllers.Thermostat import ThermostatController
from .controllers.Door import DoorController, DoorState
from .controllers.Power import PowerController, PowerState

from config import PinConfig, SystemConfig

# System constants
WATCHDOG_TIMEOUT = const(60)  # seconds
SYSTEM_CHECK_INTERVAL = const(5)  # seconds
RETRY_ATTEMPTS = const(3)

class SystemState:
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    SAFE_MODE = "safe_mode"
    MAINTENANCE = "maintenance"

class IoTController:
    def __init__(self):
        # System state
        self.state = SystemState.INITIALIZING
        self.last_system_check = 0
        self.initialization_retry = 0
        
        # Initialize core systems first
        self.event_system = EventSystem()
        self.rules_engine = RulesEngine(self.event_system)
        self.safety_monitor = SafetyMonitor(self.event_system)
        self.comm_handler = CommHandler(
            uart_id=0, 
            baudrate=SystemConfig.UART_SPEED
        )
        
        # Initialize hardware interfaces
        self.gpio = GPIOController(self.event_system)
        self.i2c = I2C(0, scl=Pin(PinConfig.I2C_SCL), sda=Pin(PinConfig.I2C_SDA))
        self.sensors = SensorManager(self.i2c)
        
        # Controller management
        self.controllers = {}
        self.command_queue = deque(maxlen=20)
        
        # System monitoring
        self.watchdog_timer = time.time()
        self.error_log = deque(maxlen=100)
        
        # Status LED
        self.status_led = Pin(PinConfig.STATUS_LED, Pin.OUT)
        
    async def initialize_system(self):
            """Initialize all system components"""
            try:
                # Step 1: Initialize Hardware
                if not await self._init_hardware():
                    raise Exception("Hardware initialization failed")
                    
                # Step 2: Initialize Controllers
                if not await self._init_controllers():
                    raise Exception("Controller initialization failed")
                    
                # Step 3: Setup Rules and Safety
                self._setup_rules()
                self._setup_safety_monitors()
                
                # Step 4: Setup Event Handlers
                self._setup_event_handlers()
                
                # Step 5: Verify Communication
                if not await self._verify_communication():
                    raise Exception("Communication verification failed")
                    
                self.state = SystemState.READY
                await self._publish_system_state()
                return True
                
            except Exception as e:
                self.error_log.append((time.time(), str(e)))
                self.initialization_retry += 1
                
                if self.initialization_retry >= RETRY_ATTEMPTS:
                    self.state = SystemState.ERROR
                    return False
                    
                # Wait and retry initialization
                await asyncio.sleep(5)
                return await self.initialize_system()
            
    async def _init_hardware(self):
        """Initialize hardware components"""
        try:
            # Setup GPIO pins
            self._setup_gpio()
            
            # Initialize sensors
            await self.sensors.initialize()
            
            # Test sensor readings
            if not await self._verify_sensors():
                return False
                
            return True
        except Exception as e:
            print(f"Hardware init error: {e}")
            return False
            
    async def _init_controllers(self):
        """Initialize system controllers"""
        try:
            # Initialize Thermostat
            self.controllers['thermostat'] = ThermostatController(
                self.gpio.get_pin('heater'),
                self.sensors,
                self.event_system
            )
            
            # Initialize Door Controller
            self.controllers['door'] = DoorController(
                self.gpio.get_pin('door'),
                self.gpio.get_pin('door_sensor'),
                self.gpio.get_pin('safety_sensor'),
                self.gpio.get_pin('motion_sensor'),
                self.gpio.get_pin('light'),
                self.event_system
            )
            
            # Initialize Power Controller
            self.controllers['power'] = PowerController(
                {name: self.gpio.get_pin(name) 
                 for name in PinConfig.POWER_OUTLETS},
                self.gpio.get_pin('current_sensor'),
                self.event_system
            )
            
            return True
        except Exception as e:
            print(f"Controller init error: {e}")
            return False
            
    def _setup_gpio(self):
        """Setup GPIO pins"""
        # Setup control pins
        self.gpio.setup_pin('heater', PinConfig.HEATER_PIN, Pin.OUT)
        self.gpio.setup_pin('door', PinConfig.DOOR_RELAY, Pin.OUT)
        
        # Setup sensor pins with interrupts where needed
        self.gpio.setup_pin(
            'door_sensor', 
            PinConfig.DOOR_SENSOR, 
            Pin.IN, 
            callback=self._handle_door_sensor,
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING
        )
        
        # Setup power control
        for i, pin in enumerate(PinConfig.POWER_OUTLETS):
            self.gpio.setup_pin(f'power_{i}', pin, Pin.OUT)
            
    async def _setup_sensors(self):
        """Setup all sensors"""
        # Add temperature sensor
        self.sensors.add_sensor(
            'temperature',
            'adc',
            pin=PinConfig.TEMP_SENSOR
        )
        
        # Test sensor readings
        initial_readings = await self.sensors.read_all()
        if not initial_readings.get('temperature'):
            raise Exception("Temperature sensor initialization failed")
            
    async def _setup_controllers(self):
        """Initialize system controllers"""
        self.controllers['thermostat'] = ThermostatController(
            self.gpio.get_pin('heater'),
            self.sensors,
            min_run_time=SystemConfig.MIN_RUN_TIME,
            cycle_delay=SystemConfig.CYCLE_DELAY
        )
        
        self.controllers['door'] = DoorController(
            self.gpio.get_pin('door'),
            self.gpio.get_pin('door_sensor'),
            timeout=SystemConfig.DOOR_TIMEOUT
        )
        
        self.controllers['power'] = PowerController(
            {f'power_{i}': self.gpio.get_pin(f'power_{i}')
             for i in range(len(PinConfig.POWER_OUTLETS))}
        )
        
    def _setup_rules(self):
        """Setup system rules"""
        # Don't run heater if door is open
        self.rules_engine.add_rule(
            'door_open_heat_off',
            lambda: not self.controllers['door'].is_open(),
            lambda: self.controllers['thermostat'].disable(),
            priority=1
        )
        
    def _setup_safety_monitors(self):
        """Setup safety monitoring"""
        # Temperature limits
        self.safety_monitor.add_condition(
            'max_temp',
            lambda: self.sensors.read_sensor('temperature') < SystemConfig.MAX_TEMP,
            severity='critical'
        )
        
    def _setup_event_handlers(self):
        """Setup system event handlers"""
        self.event_system.subscribe('temp_change', 
            self.controllers['thermostat'].handle_temp_change)
        self.event_system.subscribe('door_sensor', 
            self.controllers['door'].handle_sensor_change)
            
    async def run(self):
            """Main system loop"""
            if self.state != SystemState.READY:
                return
                
            self.state = SystemState.RUNNING
            
            while True:
                try:
                    # Update watchdog
                    self.watchdog_timer = time.time()
                    self.status_led.toggle()
                    
                    # Process communications
                    await self._handle_communications()
                    
                    # Update controllers
                    await self._update_controllers()
                    
                    # Check system state
                    await self._check_system_state()
                    
                    # Process command queue
                    await self._process_command_queue()
                    
                    # Small delay to prevent busy waiting
                    await asyncio.sleep_ms(100)
                    
                except Exception as e:
                    await self._handle_system_error(str(e))
                
    async def _update_controllers(self):
        """Update all controllers"""
        for name, controller in self.controllers.items():
            try:
                if controller.enabled:
                    await controller.update()
                    
                # Check controller watchdog
                if not controller.check_watchdog():
                    await self._handle_controller_timeout(name)
                    
            except Exception as e:
                await self._handle_controller_error(name, str(e))
                
    async def _check_system_state(self):
        """Periodic system state check"""
        current_time = time.time()
        
        if current_time - self.last_system_check >= SYSTEM_CHECK_INTERVAL:
            self.last_system_check = current_time
            
            # Check safety conditions
            if not await self.safety_monitor.check_safety():
                await self._enter_safe_mode()
                
            # Evaluate rules
            await self.rules_engine.evaluate_rules()
            
            # Check power consumption
            if self.controllers['power'].total_power > SystemConfig.MAX_POWER:
                await self._handle_power_overload()
                
            # Update system state
            await self._publish_system_state()
                
    async def _process_command_queue(self):
        """Process pending commands"""
        while self.command_queue:
            cmd = self.command_queue.popleft()
            await self._handle_command(cmd)
            
    async def _update_controllers(self):
        """Update all controllers"""
        for controller in self.controllers.values():
            if controller.enabled:
                await controller.update()
                
    async def _check_system_rules(self):
        """Check rules and safety conditions"""
        await self.rules_engine.evaluate_rules()
        if not await self.safety_monitor.check_safety():
            await self._handle_unsafe_condition()
            
    async def _send_updates(self):
        """Send state updates if needed"""
        current_time = time.time()
        if current_time - self.last_update >= SystemConfig.UPDATE_INTERVAL:
            state = self._get_system_state()
            await self.comm_handler.send_state(state)
            self.last_update = current_time
            
    def _get_system_state(self):
        """Get complete system state"""
        return {
            'system_state': self.current_state,
            'controllers': {
                name: controller.get_state() 
                for name, controller in self.controllers.items()
            },
            'sensors': await self.sensors.read_all(),
            'safety': self.safety_monitor.get_triggered_conditions()
        }
        
    async def _handle_command(self, cmd):
        """Process a single command"""
        try:
            if not isinstance(cmd, dict):
                cmd = json.loads(cmd)
                
            if cmd['type'] not in self.controllers:
                raise ValueError(f"Unknown controller type: {cmd['type']}")
                
            controller = self.controllers[cmd['type']]
            await controller.process_command(cmd['action'], cmd.get('params', {}))
            
        except Exception as e:
            print(f"Command error: {e}")
            self.event_system.publish('command_error', 
                                    {'error': str(e), 'command': cmd})
            
    async def _handle_unsafe_condition(self):
        """Handle unsafe system state"""
        self.current_state = 'safe_mode'
        
        # Shutdown controllers
        for controller in self.controllers.values():
            await controller.safe_shutdown()
            
        # Notify about unsafe condition
        await self.comm_handler.send_event(
            'safety_critical',
            {
                'state': self.current_state,
                'conditions': self.safety_monitor.get_triggered_conditions()
            }
        )

'''
#Safety
def _setup_safety_monitors(self):
    """Setup safety monitoring"""
    # Critical temperature monitoring
    self.safety_monitor.add_condition(
        name='max_temperature',
        check_func=lambda: self.sensors.read_sensor('temperature') < SystemConfig.MAX_TEMP,
        severity=SafetySeverity.CRITICAL,
        threshold=3,  # Three violations before triggering
        recovery_action=self.controllers['thermostat'].emergency_shutdown
    )

    # Door safety monitoring
    self.safety_monitor.add_condition(
        name='door_operation',
        check_func=self.controllers['door'].check_operation_safety,
        severity=SafetySeverity.HIGH,
        recovery_action=self.controllers['door'].emergency_stop
    )

    # Power monitoring
    self.safety_monitor.add_condition(
        name='power_load',
        check_func=self.controllers['power'].check_load_safety,
        severity=SafetySeverity.MEDIUM,
        recovery_action=self.controllers['power'].reduce_load
    )
'''

'''
#Comms
async def _process_communications(self):
    """Process communications"""
    # Check for incoming messages
    message = await self.comm_handler.check_messages()
    if message:
        await self._handle_incoming_message(message)
    
    # Process any retries
    await self.comm_handler.process_retries()
    
    # Check connection status
    if not self.comm_handler.check_connection():
        await self._handle_communication_loss()
'''

'''
#rules
def _setup_rules(self):
    """Setup system rules"""
    # Safety rule: Don't run heater if door is open
    self.rules_engine.add_rule(
        name='door_heater_safety',
        condition=lambda: not self.controllers['door'].is_open(),
        action=lambda: self.controllers['thermostat'].disable(),
        priority=RulePriority.CRITICAL
    )
    
    # Comfort rule: Turn on lights when door opens
    self.rules_engine.add_rule(
        name='door_lights',
        condition=lambda: self.controllers['door'].is_open(),
        action=lambda: self.controllers['power'].control_outlet('lights', True),
        priority=RulePriority.LOW,
        cooldown=300  # 5 minute cooldown
    )
    
    # Energy saving rule: Power off outlets if door closed for 1 hour
    async def check_door_time():
        return (
            not self.controllers['door'].is_open() and 
            time.time() - self.controllers['door'].last_closed > 3600
        )
    
    self.rules_engine.add_rule(
        name='power_save',
        condition=check_door_time,
        action=lambda: self.controllers['power'].power_save_mode(),
        priority=RulePriority.NORMAL
    )
'''

'''
#events
# In IoTController
async def _setup_event_handlers(self):
    # Priority handler for safety events
    self.event_system.subscribe(
        'safety_critical',
        self._handle_safety_event,
        priority=True
    )
    
    # Async handler for sensor updates
    self.event_system.subscribe(
        'sensor_update',
        self._handle_sensor_update,
        is_async=True
    )
    
    # Regular handler for status updates
    self.event_system.subscribe(
        'status_update',
        self._handle_status_update
    )

# Example event handling
async def _handle_sensor_update(self, event):
    if event.data['type'] == 'temperature':
        await self.controllers['thermostat'].handle_temp_change(event.data)
'''