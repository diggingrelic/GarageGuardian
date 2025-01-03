import os
import gc
import asyncio
from .microtest import TestCase
from ..logging.Log import debug, error

def is_test_method(name, method):
    return name.startswith('test_') and callable(method)

def is_async_method(method):
    """Check if a method is async by looking for __await__"""
    return hasattr(method, '__await__') or getattr(method, 'is_async', False)

def run_tests():
    """Run all tests from the tests directory"""
    debug("Running tests...")
    debug("=" * 40)
    
    passed = 0
    failed = 0
    
    # Get test files from tests directory
    tests_dir = "gg/testing/tests"
    
    # Import and run all test files from the tests directory
    for filename in os.listdir(tests_dir):
        if filename.startswith("test_") and filename.endswith(".py"):
            module_name = filename[:-3]  # Remove .py
            try:
                # Import the test module
                module = __import__("gg.testing.tests." + module_name)
                module = getattr(module.testing.tests, module_name)
                
                # Find test classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, TestCase) and attr != TestCase:
                        debug(f"\nRunning {attr_name}:")
                        test_instance = attr()
                        
                        # Find and run test methods
                        for method_name in dir(test_instance):
                            if method_name.startswith('test_'):
                                method = getattr(test_instance, method_name)
                                if callable(method):
                                    try:
                                        message = f"  {method_name}..."
                                        if is_async_method(method):
                                            asyncio.run(method())
                                        else:
                                            method()
                                        debug(f"{message} ✓")
                                        passed += 1
                                    except Exception as e:
                                        debug(f"{message} ✗ ({str(e)})")
                                        failed += 1
                                    finally:
                                        test_instance.tearDown()  # Always call tearDown
                        
                        # Remove cleanup since we now use tearDown
                        gc.collect()  # Still good to collect garbage between test classes
            except Exception as e:
                error(f"Error loading tests from {filename}: {e}")
                failed += 1
            
            gc.collect()
    
    debug("=" * 40)
    debug(f"Tests complete: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == '__main__':
    run_tests()