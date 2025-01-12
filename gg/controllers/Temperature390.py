from ..devices.bmp390 import BMP390
from ..logging.Log import debug, error
from machine import I2C, Pin # type: ignore

class Temperature390:
    """Temperature controller for BMP390 sensor
    
    Handles temperature, pressure, and altitude readings
    with appropriate unit conversions.
    """
    
    def __init__(self, i2c=None):
        """Initialize BMP390 controller
        Args:
            i2c: Optional I2C instance. If None, will create default
        """
        try:
            # Initialize I2C if not provided
            if i2c is None:
                i2c = I2C(0, sda=Pin(4), scl=Pin(5))
            
            self.hardware = BMP390(i2c)
            debug("BMP390 temperature sensor initialized")
            
        except Exception as e:
            error(f"Failed to initialize BMP390: {e}")
            raise
            
    def get_fahrenheit(self):
        """Get temperature in Fahrenheit"""
        try:
            celsius = self.hardware.read_temperature()
            return (celsius * 9/5) + 32
        except Exception as e:
            error(f"Failed to read temperature: {e}")
            return None
            
    def get_pressure(self):
        """Get pressure in hPa (hectopascals)"""
        try:
            pascals = self.hardware.read_pressure()
            return pascals / 100  # Convert Pa to hPa
        except Exception as e:
            error(f"Failed to read pressure: {e}")
            return None
            
    def get_altitude(self):
        """Get altitude in feet"""
        try:
            meters = self.hardware.read_altitude()
            return meters * 3.28084  # Convert meters to feet
        except Exception as e:
            error(f"Failed to read altitude: {e}")
            return None
            
    def get_all_readings(self):
        """Get all sensor readings at once
        Returns:
            dict: Temperature (°F), Pressure (hPa), Altitude (ft)
        """
        try:
            temp, press = self.hardware.read()
            alt = self.hardware.read_altitude()
            
            return {
                "temperature": (temp * 9/5) + 32,
                "pressure": press / 100,
                "altitude": alt * 3.28084
            }
        except Exception as e:
            error(f"Failed to read sensor values: {e}")
            return None 