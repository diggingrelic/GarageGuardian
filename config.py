# config.py
class PinConfig:
    """Pin assignments for hardware connections"""
    # I2C Bus
    I2C_SDA = 4
    I2C_SCL = 5
    
    # Relay Controls
    RELAY_PINS = {
        'HEATER': 15,
        'GARAGE_DOOR_1': 14,
        'GARAGE_DOOR_2': None,  # Future use
        'GARAGE_DOOR_3': None,  # Future use
    }
    
    # Sensors
    SENSOR_PINS = {
        'MOTION': 18,
        'DOOR': 17,
    }
    
    # Status LEDs
    STATUS_LEDS = {
        'HEATER': "LED",  # Using onboard LED for now
        'NETWORK': None,  # Future use
        'SYSTEM': None,   # Future use
    }

class I2CConfig:
    """I2C bus configuration"""
    FREQUENCY = 400000  # 400kHz
    TIMEOUT = 50000     # 50ms timeout

class SystemConfig:
    """System-wide settings"""
    _instance = None
    STATE_VERSION = 1
    
    # Define all class-level defaults
    TEMP_SETTINGS = {
        'MIN_TEMP': 40,     # Fahrenheit
        'MAX_TEMP': 90,     # Fahrenheit
        'MIN_RUN_TIME': 300,  # 5 minutes
        'CYCLE_DELAY': 180,   # 3 minutes
        'DEFAULT_SETPOINT': 72,  # Default target temperature
        'TEMP_DIFFERENTIAL': 2.0,  # Changed to 2°F
        'TARGET_TEMP': 72,    # Current target temperature
        'HEATER_MODE': 'off'  # Current heater mode (off/heat)
    }
    
    TIMER_SETTINGS = {
        'END_TIME': None,     # Unix timestamp for timer end
        'DURATION': None      # Timer duration in hours
    }
    
    # Define all class-level defaults that might be accessed before instantiation
    UPDATE_INTERVALS = {
        'TEMPERATURE': 5,     # seconds
        'HEATER_CHECK': 30,   # seconds
        'SAFETY_CHECK': 5,    # seconds
    }
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if SystemConfig._instance is not None:
            raise RuntimeError("Use get_instance() instead")
            
        # Copy class defaults to instance
        self.TEMP_SETTINGS = SystemConfig.TEMP_SETTINGS.copy()
        self.UPDATE_INTERVALS = SystemConfig.UPDATE_INTERVALS.copy()
        
        # Safety
        self.MAX_RETRIES = 3
        
        # Hardware settings
        self.HARDWARE = {
            'I2C_RETRY_COUNT': 3,
            'I2C_RETRY_DELAY': 0.1,  # seconds
        }
        
        SystemConfig._instance = self
        
    def update_setting(self, category, setting, value):
        """Update a setting and notify all listeners"""
        if hasattr(self, category):
            settings = getattr(self, category)
            if setting in settings:
                old_value = settings[setting]
                settings[setting] = value
                return True, old_value
        return False, None

class LogConfig:
    """Logging configuration"""
    DEBUG = True  # Set to False in production
    LOG_LEVEL = "DEBUG"  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    RUN_TESTS = True
    TEST_DELAY = 2  # Seconds to wait after test failures
