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
    
    # Status
    STATUS_LED = "LED"

class I2CConfig:
    """I2C device configurations"""
    # Bus configuration
    FREQUENCY = 100000  # 100kHz standard mode
    
    # Device addresses
    ADDRESSES = {
        'TEMP_INDOOR': 0x48,    # ADT7410
        'TEMP_OUTDOOR': None,   # Future use
        'TEMP_PROCESS': None,   # Future use
    }

class SPIConfig:
    """SPI device configurations"""
    # Reserved for future use
    pass

class UARTConfig:
    """UART device configurations"""
    UART_TX = 6
    UART_RX = 7
    BAUD_RATE = 115200

class SystemConfig:
    """System-wide settings"""
    # Thermostat settings
    TEMP_SETTINGS = {
        'MIN_TEMP': 5,
        'MAX_TEMP': 30,
        'MIN_RUN_TIME': 300,  # 5 minutes
        'CYCLE_DELAY': 180,   # 3 minutes
        'DEFAULT_SETPOINT': 20,
        'TEMP_DIFFERENTIAL': 1.0,
    }
    
    # Update intervals
    UPDATE_INTERVALS = {
        'TEMPERATURE': 60,    # seconds
        'HEATER_CHECK': 30,   # seconds
        'SAFETY_CHECK': 5,    # seconds
    }
    
    # Safety
    MAX_RETRIES = 3

class LogConfig:
    """Logging configuration"""
    DEBUG = True  # Set to False in production
    LOG_LEVEL = "DEBUG"  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    RUN_TESTS = True
    TEST_DELAY = 2  # Seconds to wait after test failures 