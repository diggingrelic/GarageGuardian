from .IoTController import IoTController
from .core.Events import EventSystem
from .core.Rules import RulesEngine
from .core.Safety import SafetyMonitor
from .core.Comms import CommHandler

__version__ = '1.0.0'

def create_garage_os():
    """Factory function to create GarageOS instance"""
    event_system = EventSystem()
    rules_engine = RulesEngine()
    safety_monitor = SafetyMonitor()
    comm_handler = CommHandler()
    
    return IoTController(
        event_system=event_system,
        rules_engine=rules_engine,
        safety_monitor=safety_monitor,
        comm_handler=comm_handler
    )