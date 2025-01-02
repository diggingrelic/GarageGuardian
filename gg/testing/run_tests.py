import gc
import asyncio

def is_test_method(name, obj):
    """Check if a method is a test method"""
    return name.startswith('test_') and callable(obj)

def is_async_method(obj):
    """Check if a method is async"""
    return hasattr(obj, '__await__') or hasattr(obj, '_is_coroutine')

def run_tests():
    print("\nRunning tests...")
    print("=" * 40)
    
    from .test_events import TestEvents
    from .test_iot_controller import TestIoTController
    from .test_rules import TestRules
    
    passed = 0
    failed = 0
    
    # Run Event Tests
    print("\nRunning Event Tests:")
    event_tests = TestEvents()
    
    for name, method in event_tests.__class__.__dict__.items():
        if is_test_method(name, method):
            if name == 'test_handler':  # Skip helper method
                continue
            try:
                print(f"  {name}...", end=" ")
                bound_method = getattr(event_tests, name)
                if is_async_method(bound_method):
                    asyncio.run(bound_method())
                    print(f"\n  {name}... ", end="")
                else:
                    bound_method()
                print("✓")
                passed += 1
            except Exception as e:
                print(f"✗ ({str(e)})")
                failed += 1
    
    # Run IoTController Tests
    print("\nRunning IoTController Tests:")
    iot_tests = TestIoTController()
    
    for name, method in iot_tests.__class__.__dict__.items():
        if is_test_method(name, method):
            try:
                print(f"  {name}...", end=" ")
                bound_method = getattr(iot_tests, name)
                if is_async_method(bound_method):
                    asyncio.run(bound_method())
                    print(f"\n  {name}... ", end="")
                else:
                    bound_method()
                print("✓")
                passed += 1
            except Exception as e:
                print(f"✗ ({str(e)})")
                failed += 1
                
    # Run Rules Tests
    print("\nRunning Rules Tests:")
    rules_tests = TestRules()
    
    for name, method in rules_tests.__class__.__dict__.items():
        if is_test_method(name, method):
            try:
                print(f"  {name}...", end=" ")
                bound_method = getattr(rules_tests, name)
                if is_async_method(bound_method):
                    asyncio.run(bound_method())
                    print(f"\n  {name}... ", end="")
                else:
                    bound_method()
                print("✓")
                passed += 1
            except Exception as e:
                print(f"✗ ({str(e)})")
                failed += 1
    
    # Clean up
    gc.collect()
    
    print("\n" + "=" * 40)
    print(f"Tests complete: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == '__main__':
    run_tests()