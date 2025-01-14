from machine import I2C, Pin # type: ignore
from ..devices.TempSensor import BMP390Service
from ..devices.HeaterRelay import HeaterRelay
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
            bmp390_service = BMP390Service(self.i2c)
            heater_relay = HeaterRelay()
            
            # Create and initialize controllers
            if not await bmp390_service.initialize():
                error("Failed to initialize BMP390 service")
                return False
            controller.register_service("bmp390", bmp390_service)
                    
            thermostat = ThermostatController(
                "thermostat",
                heater_relay,
                controller.safety,
                controller.events
            )
            if not await thermostat.initialize():
                error("Failed to initialize thermostat")
                return False

            controller.register_device("thermostat", thermostat)
            
            return True
            
        except Exception as e:
            error(f"Device creation failed: {e}")
            return False 