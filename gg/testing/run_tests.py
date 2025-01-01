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
    
    # Clean up
    gc.collect()
    
    print("\n" + "=" * 40)
    print(f"Tests complete: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == '__main__':
    run_tests()