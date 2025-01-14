from ..microtest import TestCase
from machine import I2C, Pin # type: ignore
from ...devices.TempSensor import BMP390Service
from config import PinConfig, I2CConfig
from ...logging.Log import debug, error

class TestBMP390Hardware(TestCase):
    """Hardware integration tests for BMP390 sensor"""
    
    def __init__(self):
        """Initialize the test case"""
        super().__init__()
        self.i2c = None
        self.sensor = None
    
    async def setUp(self):
        """Initialize test components"""
        try:
            self.i2c = I2C(0, 
                          scl=Pin(PinConfig.I2C_SCL), 
                          sda=Pin(PinConfig.I2C_SDA), 
                          freq=I2CConfig.FREQUENCY)
            self.sensor = BMP390Service(self.i2c)
        except Exception as e:
            error(f"Setup failed: {e}")
            raise
            
    async def tearDown(self):
        """Clean up after test"""
        self.sensor = None
        self.i2c = None
        
    async def test_sensor_readings(self):
        """Test BMP390 sensor readings"""
        debug("=== Testing BMP390 Sensor ===")
        
        try:
            # Get temperature
            temp_f = self.sensor.get_fahrenheit()
            self.assertTrue(temp_f is not None, "Failed to get temperature reading")
            debug(f"Temperature: {temp_f:.1f}°F")
            
            # Basic sanity check (-10°F to 120°F)
            self.assertTrue(-10 <= temp_f <= 120, 
                          f"Temperature {temp_f}°F outside reasonable range")
            
            # Get pressure
            pressure = self.sensor.get_pressure()
            self.assertTrue(pressure is not None, "Failed to get pressure reading")
            debug(f"Pressure: {pressure:.1f} hPa")
            
            # Reasonable pressure range (800-1100 hPa covers most elevations)
            self.assertTrue(800 <= pressure <= 1100,
                          f"Pressure {pressure} hPa outside reasonable range")
            
            # Get altitude
            altitude = self.sensor.get_altitude()
            self.assertTrue(altitude is not None, "Failed to get altitude reading")
            debug(f"Altitude: {altitude:.1f} ft")
            
            # Reasonable altitude range (-1000 to 10000 ft)
            self.assertTrue(-1000 <= altitude <= 10000,
                          f"Altitude {altitude} ft outside reasonable range")
            
            # Check sensor health
            self.assertTrue(await self.sensor.is_working(),
                          "Sensor health check failed")
            
            debug("Temperature sensor test passed!")
            
        except Exception as e:
            error(f"Temperature sensor test failed: {e}")
            raise 