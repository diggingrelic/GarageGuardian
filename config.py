# config.py
class PinConfig:
    # Thermostat
    HEATER_PIN = 15
    TEMP_SENSOR = 16
    
    # Door Control
    DOOR_RELAY = 14
    DOOR_SENSOR = 17
    MOTION_SENSOR = 18
    
    # Power Control
    POWER_OUTLETS = [19, 20, 21, 22]
    
    # Communication
    UART_TX = 6
    UART_RX = 7
    
    # LED Status
    STATUS_LED = "LED"

    # I2C
    I2C_SDA = 4
    I2C_SCL = 5

class LogConfig:
    DEBUG = True  # Set to False in production
    RUN_TESTS = True
    TEST_DELAY = 2  # Seconds to wait after test failures

class SystemConfig:
    # Thermostat settings
    MIN_TEMP = 5
    MAX_TEMP = 30
    MIN_RUN_TIME = 300  # 5 minutes
    CYCLE_DELAY = 180   # 3 minutes
    
    # Door settings
    DOOR_TIMEOUT = 30   # seconds
    
    # Communication
    UART_SPEED = 115200
    UPDATE_INTERVAL = 5  # seconds

    # Safety
    MAX_RETRIES = 3
