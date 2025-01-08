from machine import I2C, Pin # type: ignore
from ..devices.TempSensor import TempSensorADT7410
from ..devices.HeaterRelay import HeaterRelay
from ..controllers.Temperature import TemperatureController
from ..controllers.Thermostat import ThermostatController
from config import PinConfig, I2CConfig
from ..logging.Log import error

class DeviceFactory:
    def __init__(self, i2c=None):
        self.i2c = i2c or self._create_default_i2c()
        
    def _create_default_i2c(self):
        return I2C(0, 
                  scl=Pin(PinConfig.I2C_SCL), 
                  sda=Pin(PinConfig.I2C_SDA),
                  freq=I2CConfig.FREQUENCY)
                  
    async def create_devices(self, controller):
        try:
            # Create hardware interfaces
            temp_sensor = TempSensorADT7410(self.i2c)
            heater_relay = HeaterRelay()
            
            # Create and initialize controllers
            temp_controller = TemperatureController(
                "temperature",
                temp_sensor,
                controller.safety,
                controller.events
            )
            if not await temp_controller.initialize():
                error("Failed to initialize temperature controller")
                return False
                
            thermostat = ThermostatController(
                "thermostat",
                heater_relay,
                controller.safety,
                controller.events
            )
            if not await thermostat.initialize():
                error("Failed to initialize thermostat")
                return False
            
            # Register with controller
            controller.register_device("temperature", temp_controller)
            controller.register_device("thermostat", thermostat)
            
            return True
            
        except Exception as e:
            error(f"Device creation failed: {e}")
            return False 