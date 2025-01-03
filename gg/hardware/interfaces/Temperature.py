from abc import abstractmethod
from typing import Tuple
from .Base import BaseDevice

class TemperatureDevice(BaseDevice):
    """Interface for temperature sensor hardware"""
    
    @abstractmethod
    def read(self) -> Tuple[float, float]:
        """Read current temperature and humidity
        
        Returns:
            Tuple[float, float]: (temperature in C, humidity percentage)
        """
        pass 