# config.py

class I2CConfig:
    """I2C bus configuration"""
    FREQUENCY = 400000  # 400kHz
    TIMEOUT = 50000     # 50ms timeout

class LogConfig:
    """Logging configuration"""
    DEBUG = True  # Set to False in production
    LOG_LEVEL = "DEBUG"  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    RUN_TESTS = False
    TEST_DELAY = 2  # Seconds to wait after test failures

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

class SystemConfig:
    """System-wide settings"""
    _instance = None
    STATE_VERSION = 1
    
    TEMP_SETTINGS = {
        'MIN_RUN_TIME': 30, #seconds
        'CYCLE_DELAY': 10, #seconds
        'TEMP_DIFFERENTIAL': 2.0, #degrees
        'SETPOINT': 90, #degrees
        'HEATER_MODE': 'off'  # Current heater mode (off/heat)
    }
    
    TIMER_SETTINGS = {
        'END_TIME': None,     # Unix timestamp for timer end
        'DURATION': None      # Timer duration in hours
    }
    
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
        
        SystemConfig._instance = self

    def update_setting(self, category, setting, value):
        settings = getattr(SystemConfig, category, None)
        if settings is None or setting not in settings:
            return False, None
            
        old_value = settings[setting]
        settings[setting] = value
        
        return True, old_value
