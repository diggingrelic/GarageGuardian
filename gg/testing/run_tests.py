import gc
import asyncio

def run_tests():
    print("\nRunning tests...")
    print("=" * 40)
    
    from .test_events import TestEvents
    from .test_iot_controller import TestIoTController
    
    passed = 0
    failed = 0
    
    # Run Event Tests
    print("\nRunning Event Tests:")
    event_tests = TestEvents()
    
    test_methods = [
        ('test_subscribe', False),
        ('test_subscribe_limit', False),
        ('test_publish', True),
        ('test_multiple_subscribers', True),
        ('test_get_stats', False),
        ('test_state_transitions', True)
    ]
    
    for method_name, is_async in test_methods:
        try:
            print(f"  {method_name}...", end=" ")
            method = getattr(event_tests, method_name)
            if is_async:
                asyncio.run(method())
            else:
                method()
            print("✓")
            passed += 1
        except Exception as e:
            print(f"✗ ({str(e)})")
            failed += 1
    
    # Run IoTController Tests
    print("\nRunning IoTController Tests:")
    iot_tests = TestIoTController()
    
    iot_test_methods = [
        ('test_init', False),
        ('test_initialize', True),
        ('test_error_handling', True)
    ]
    
    for method_name, is_async in iot_test_methods:
        try:
            print(f"  {method_name}...", end=" ")
            method = getattr(iot_tests, method_name)
            if is_async:
                asyncio.run(method())
                print(f"  {method_name}... ", end="")  # Reprint test name
            else:
                method()
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