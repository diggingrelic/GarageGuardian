import sys
import asyncio
from .test_thermostat_system import TestThermostatSystem
from .test_bmp390_hardware import TestBMP390Hardware
from .file_logger_tests import run_cowbell_logger_tests
from ...logging.Log import debug, error

async def run_tests(controller, settings_manager):
    """Run hardware integration tests"""
    debug("=== Hardware Integration Tests ===")
    passed = failed = 0
    
    try:
        # Test BMP390 sensor
        debug("\n=== Testing BMP390 Sensor ===")
        bmp_test = TestBMP390Hardware()
        await bmp_test.setUp()
        await bmp_test.test_sensor_readings()
        await bmp_test.tearDown()
        passed += 1
        
        # Test thermostat system
        debug("\n=== Testing Thermostat System ===")
        therm_test = TestThermostatSystem(controller, settings_manager)
        
        # Test cycle delay
        await therm_test.setUp()
        await therm_test.test_cycle_delay_enforcement()
        await therm_test.tearDown()
        passed += 1
        
        # Test timed heating
        await therm_test.setUp()
        await therm_test.test_timed_heating()
        await therm_test.tearDown()
        passed += 1
        
        # Run cowbell logger tests
        debug("\n=== Running Cowbell Logger Tests ===")
        try:
            run_cowbell_logger_tests()
            passed += 1
        except Exception as e:
            error(f"Logger test failed: {e}")
            failed += 1
        
    except Exception as e:
        error(f"Test failed: {e}")
        failed += 1
        try:
            await therm_test.tearDown()
        except Exception as e:
            error(f"Teardown failed: {e}")
            
    debug(f"Results: {passed} passed, {failed} failed")
    return passed, failed

def main():
    """Main entry point"""
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        debug("Tests cancelled by user")
    except Exception as e:
        error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 