import sys
import asyncio
from ..microtest import TestCase
from .test_thermostat_system import TestThermostatSystem
from ...logging.Log import debug, error

async def run_tests(controller):
    """Run hardware integration tests"""
    debug("=== Hardware Integration Tests ===")
    passed = failed = 0
    
    test = TestThermostatSystem(controller)
    
    try:
        await test.setUp()
        await test.test_cycle_delay_enforcement()
        await test.tearDown()
        passed += 1
    except Exception as e:
        error(f"Test failed: {e}")
        failed += 1
        try:
            await test.tearDown()
        except Exception as e:
            error(f"Teardown failed: {e}")
            
    debug(f"\nResults: {passed} passed, {failed} failed")
    return passed, failed

def main():
    """Main entry point"""
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 