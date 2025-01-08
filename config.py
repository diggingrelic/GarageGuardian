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
    # Thermostat settings
    TEMP_SETTINGS = {
        'MIN_TEMP': 40,     # Fahrenheit
        'MAX_TEMP': 90,     # Fahrenheit
        'MIN_RUN_TIME': 300,  # 5 minutes
        'CYCLE_DELAY': 180,   # 3 minutes
        'DEFAULT_SETPOINT': 72,  # Changed to 72°F
        'TEMP_DIFFERENTIAL': 2.0,  # Changed to 2°F
    }
    
    # Update intervals
    UPDATE_INTERVALS = {
        'TEMPERATURE': 5,     # seconds
        'HEATER_CHECK': 30,   # seconds
        'SAFETY_CHECK': 5,    # seconds
    }
    
    # Safety
    MAX_RETRIES = 3
    
    # Hardware settings
    HARDWARE = {
        'I2C_RETRY_COUNT': 3,
        'I2C_RETRY_DELAY': 0.1,  # seconds
    }

class LogConfig:
    """Logging configuration"""
    DEBUG = True  # Set to False in production
    LOG_LEVEL = "DEBUG"  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    RUN_TESTS = True
    TEST_DELAY = 2  # Seconds to wait after test failures
