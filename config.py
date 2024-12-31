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
    UART_TX = 0
    UART_RX = 1
    
    # LED Status
    STATUS_LED = 25

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