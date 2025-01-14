"""
Test script for BMP390 sensor that prints raw and calibrated values for debugging
"""
from machine import I2C, Pin # type: ignore
from ...devices.bmp390 import BMP390
import time

def test_bmp390():
   print("Starting BMP390 test...")
   
   # Initialize I2C
   i2c = I2C(0, sda=Pin(4), scl=Pin(5))
   devices = [hex(device) for device in i2c.scan()]
   print(f"I2C devices found: {devices}")
   
   try:
       # Initialize sensor
       bmp = BMP390(i2c)
       print("BMP390 initialized successfully!")
       
       # Read and print calibration coefficients
       print("\nCalibration coefficients:")
       print("Temperature:")
       print(f"T1: {bmp._temp_calib[0]}")
       print(f"T2: {bmp._temp_calib[1]}")
       print(f"T3: {bmp._temp_calib[2]}")
       
       print("\nPressure:")
       for i, coef in enumerate(bmp._pressure_calib):
           print(f"P{i+1}: {coef}")
           
       # Take multiple readings with raw values
       print("\nTaking readings:")
       for i in range(5):
           # Read raw ADC values first 
           data = bmp._read_register(bmp._REGISTER_PRESSUREDATA, 6)
           raw_press = data[2] << 16 | data[1] << 8 | data[0]
           raw_temp = data[5] << 16 | data[4] << 8 | data[3]
           
           # Now get compensated values
           temp, press = bmp.read()
           altitude = bmp.read_altitude()
           
           print(f"\nReading {i + 1}:")
           print(f"Raw ADC values:")
           print(f"  Temperature: 0x{raw_temp:06x} ({raw_temp})")
           print(f"  Pressure: 0x{raw_press:06x} ({raw_press})")
           print(f"Compensated values:")
           print(f"  Temperature: {temp:.2f}°C")
           print(f"  Pressure: {press/100:.1f} hPa")
           print(f"  Altitude: {altitude:.1f} m")
           
           time.sleep(1)
           
   except Exception as e:
       print(f"Error: {str(e)}")
       import sys
       sys.print_exception(e)

if __name__ == "__main__":
   test_bmp390()