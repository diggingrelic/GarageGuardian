from machine import Pin # type: ignore
from .Interfaces import PinInterface, DoorInterface
import asyncio

class MachinePin(PinInterface):
    """Real hardware implementation using machine.Pin"""
    def __init__(self, pin_id, mode):
        super().__init__(pin_id)
        self._pin = Pin(pin_id, mode)
        
    def set_high(self):
        self._pin.value(1)
        
    def set_low(self):
        self._pin.value(0)
        
    def read(self):
        return self._pin.value()

class MachineDoor(DoorInterface):
    """Real hardware implementation for garage door"""
    def __init__(self, gpio_manager, relay_pin, position_pin, obstruction_pin):
        super().__init__()
        self.gpio = gpio_manager
        
        # Setup pins
        self.gpio.setup("door_relay", relay_pin, gpio_manager.OUT)
        self.gpio.setup("door_position", position_pin, gpio_manager.IN)
        self.gpio.setup("door_obstruction", obstruction_pin, gpio_manager.IN)
        
        self.relay = "door_relay"
        self.position_sensor = "door_position"
        self.obstruction_sensor = "door_obstruction"
        
    async def open(self):
        self.gpio.write(self.relay, True)
        await asyncio.sleep_ms(500)  # Pulse the relay
        self.gpio.write(self.relay, False)
        
    async def close(self):
        self.gpio.write(self.relay, True)
        await asyncio.sleep_ms(500)  # Pulse the relay
        self.gpio.write(self.relay, False)
        
    async def stop(self):
        self.gpio.write(self.relay, False)
        
    def is_fully_open(self):
        return self.gpio.read(self.position_sensor) == 1
        
    def is_fully_closed(self):
        return self.gpio.read(self.position_sensor) == 0
        
    def is_obstructed(self):
        return self.gpio.read(self.obstruction_sensor) == 1 