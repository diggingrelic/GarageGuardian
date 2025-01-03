import gc
import asyncio
import time
from ..logging.Log import debug, info

def is_test_method(name, obj):
    """Check if a method is a test method"""
    return name.startswith('test_') and callable(obj)

def is_async_method(obj):
    """Check if a method is async"""
    return hasattr(obj, '__await__') or hasattr(obj, '_is_coroutine')

def run_tests():
    debug("Running tests...")
    debug("=" * 40)
    
    from .test_events import TestEvents
    from .test_iot_controller import TestIoTController
    from .test_rules import TestRules
    from .test_logging import TestLogging
    
    passed = 0
    failed = 0
    
    # Run Event Tests
    debug("Running Event Tests:")
    event_tests = TestEvents()
    
    for name, method in event_tests.__class__.__dict__.items():
        if is_test_method(name, method):
            if name == 'test_handler':  # Skip helper method
                continue
            try:
                message = f"  {name}..."
                bound_method = getattr(event_tests, name)
                if is_async_method(bound_method):
                    asyncio.run(bound_method())
                    message = f"\n  {name}..."
                else:
                    bound_method()
                debug(f"{message} ✓")
                passed += 1
            except Exception as e:
                debug(f"{message} ✗ ({str(e)})")
                failed += 1
    
    # Run IoTController Tests
    debug("Running IoTController Tests:")
    iot_tests = TestIoTController()
    
    for name, method in iot_tests.__class__.__dict__.items():
        if is_test_method(name, method):
            try:
                message = f"  {name}..."
                bound_method = getattr(iot_tests, name)
                if is_async_method(bound_method):
                    asyncio.run(bound_method())
                    message = f"\n  {name}..."
                else:
                    bound_method()
                debug(f"{message} ✓")
                passed += 1
            except Exception as e:
                debug(f"{message} ✗ ({str(e)})")
                failed += 1
                
    # Run Rules Tests
    debug("Running Rules Tests:")
    rules_tests = TestRules()
    
    for name, method in rules_tests.__class__.__dict__.items():
        if is_test_method(name, method):
            try:
                message = f"  {name}..."
                bound_method = getattr(rules_tests, name)
                if is_async_method(bound_method):
                    asyncio.run(bound_method())
                    message = f"\n  {name}..."
                else:
                    bound_method()
                debug(f"{message} ✓")
                passed += 1
            except Exception as e:
                debug(f"{message} ✗ ({str(e)})")
                failed += 1

    # Run Logging Tests
    debug("Running Logging Tests:")
    logging_tests = TestLogging()
    
    for name, method in logging_tests.__class__.__dict__.items():
        if is_test_method(name, method):
            try:
                message = f"  {name}..."
                bound_method = getattr(logging_tests, name)
                if is_async_method(bound_method):
                    asyncio.run(bound_method())
                    message = f"\n  {name}..."
                else:
                    bound_method()
                debug(f"{message} ✓")
                passed += 1
            except Exception as e:
                debug(f"{message} ✗ ({str(e)})")
                failed += 1
    
    # Clean up
    gc.collect()
    
    debug("=" * 40)
    debug(f"Tests complete: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == '__main__':
    run_tests()