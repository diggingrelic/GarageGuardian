from machine import ADC, I2C
from time import time
from collections import deque

class SensorManager:
    def __init__(self, i2c=None):
        self.sensors = {}
        self.history = {}
        self.i2c = i2c or I2C(0, freq=400000)
        
    def add_sensor(self, name, sensor_type, pin=None, address=None):
        """Add a new sensor"""
        if sensor_type == 'adc':
            sensor = ADC(pin)
        elif sensor_type == 'i2c':
            # Implement specific I2C sensor initialization
            pass
        
        self.sensors[name] = {
            'type': sensor_type,
            'sensor': sensor,
            'last_reading': None,
            'address': address
        }
        self.history[name] = deque(maxlen=100)
        
    async def read_sensor(self, name):
        """Read a specific sensor"""
        if name not in self.sensors:
            return None
            
        sensor_info = self.sensors[name]
        reading = None
        
        try:
            if sensor_info['type'] == 'adc':
                reading = sensor_info['sensor'].read_u16()
            elif sensor_info['type'] == 'i2c':
                # Implement specific I2C sensor reading
                pass
                
            # Store reading
            if reading is not None:
                sensor_info['last_reading'] = reading
                self.history[name].append((time(), reading))
                
            return reading
            
        except Exception as e:
            print(f"Sensor read error ({name}): {e}")
            return None
            
    async def read_all(self):
        """Read all sensors"""
        readings = {}
        for name in self.sensors:
            readings[name] = await self.read_sensor(name)
        return readings
        
    def get_history(self, name, limit=None):
        """Get sensor history"""
        if name not in self.history:
            return []
        return list(self.history[name])[-limit:] if limit else list(self.history[name])