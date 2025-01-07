from ..microtest import TestCase
from ...devices.TempSensorADT7410 import TempSensorADT7410
from ...config import I2CConfig, PinConfig
from machine import I2C, Pin # type: ignore
import time

class TestTempSensorHardware(TestCase):
    """Hardware integration tests for ADT7410 temperature sensor"""
    
    def setUp(self):
        # Initialize I2C with correct frequency
        self.i2c = I2C(0, 
                       scl=Pin(PinConfig.I2C_SCL), 
                       sda=Pin(PinConfig.I2C_SDA), 
                       freq=I2CConfig.FREQUENCY)
        self.sensor = TempSensorADT7410(self.i2c)  # No address needed in constructor
        
    async def test_sensor_presence(self):
        """Verify sensor is responding on I2C bus"""
        devices = self.i2c.scan()
        print(f"\nDetected I2C devices: {[hex(d) for d in devices]}")
        self.assertTrue(len(devices) > 0, "No I2C devices detected")
        
    async def test_temperature_reading(self):
        """Verify temperature readings with retries"""
        print("\nAttempting to read temperature...")
        
        for attempt in range(5):
            temp_f = self.sensor.get_fahrenheit()
            if temp_f is not None:
                print(f"Temperature reading: {temp_f}°F")
                # Basic sanity check for reasonable indoor temperature
                self.assertTrue(20 <= temp_f <= 120, 
                              f"Temperature {temp_f}°F outside reasonable range")
                break
        else:
            self.fail("Failed to get valid temperature reading after 5 attempts")
        
        # Manual verification
        response = input("\nDoes this temperature reading look correct? (y/n): ")
        self.assertEqual(response.lower(), 'y')
        
    async def test_reading_stability(self):
        """Check temperature reading stability"""
        print("\nTaking multiple readings over 5 seconds...")
        readings = []
        
        for _ in range(5):
            temp = self.sensor.get_fahrenheit()
            if temp is not None:
                readings.append(temp)
                print(f"Reading: {temp}°F")
                time.sleep(1)
            else:
                print("Failed reading, retrying...")
                
        self.assertTrue(len(readings) > 0, "No valid readings obtained")
        
        if len(readings) > 1:
            max_diff = max(abs(readings[i] - readings[i-1]) 
                         for i in range(1, len(readings)))
            print(f"Maximum difference between consecutive readings: {max_diff}°F")
            self.assertLess(max_diff, 2.0, "Excessive temperature fluctuation detected")
        
        response = input("\nDo these readings look stable and reasonable? (y/n): ")
        self.assertEqual(response.lower(), 'y') 