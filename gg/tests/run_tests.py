import gc
import asyncio

def run_tests():
    print("\nRunning tests...")
    print("=" * 40)
    
    # Import test modules
    from tests.test_events import TestEvents
    from tests.test_iot_controller import TestIoTController
    
    # Create test instances
    event_tests = TestEvents()
    iot_tests = TestIoTController()
    
    passed = 0
    failed = 0
    
    # Run Event Tests
    print("\nRunning Event Tests:")
    try:
        print("  test_subscribe...", end=" ")
        event_tests.test_subscribe()
        print("✓")
        passed += 1
    except Exception as e:
        print(f"✗ ({str(e)})")
        failed += 1
        
    try:
        print("  test_publish...", end=" ")
        asyncio.run(event_tests.test_publish())
        print("✓")
        passed += 1
    except Exception as e:
        print(f"✗ ({str(e)})")
        failed += 1
    
    # Run IoTController Tests
    print("\nRunning IoTController Tests:")
    try:
        print("  test_init...", end=" ")
        iot_tests.test_init()
        print("✓")
        passed += 1
    except Exception as e:
        print(f"✗ ({str(e)})")
        failed += 1
        
    try:
        print("  test_initialize...", end=" ")
        asyncio.run(iot_tests.test_initialize())
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