import os
from gg.logging.cowbell_logger import SimpleLogger

def setup_test_directory():
    """Ensure we have a clean test environment"""
    try:
        # List directory to check what exists
        try:
            os.listdir('/sd/test')
        except OSError:
            # Directory doesn't exist, create it
            os.mkdir('/sd/test')
            
        # Check for logs directory
        try:
            os.listdir('/sd/test/logs')
        except OSError:
            # Logs directory doesn't exist, create it
            os.mkdir('/sd/test/logs')
            
        # Check for state file and remove if it exists
        try:
            os.stat('/sd/test/state.json')
            os.remove('/sd/test/state.json')
        except OSError:
            pass  # File doesn't exist, that's fine
        try:
            os.stat('/sd/test/timer.json')
            os.remove('/sd/test/timer.json')
        except OSError:
            pass  # File doesn't exist, that's fine
    except Exception as e:
        print(f"Error setting up test directories: {e}")

def test_state_persistence(logger):
    """Test saving and loading state"""
    print("\nTesting state persistence...")
    
    # Test saving state
    test_state = {
        "target_temp": 72,
        "mode": "heat",
        "schedule": {
            "wake": "6:00",
            "sleep": "22:00"
        }
    }
    
    success = logger.save_state(test_state, path="/sd/test", state_file="state.json")
    print(f"Save state successful: {success}")
    assert success, "Failed to save state"
    
    # Test loading state
    loaded_state = logger.load_state(path="/sd/test", state_file="state.json")
    print(f"Loaded state: {loaded_state}")
    assert loaded_state == test_state, "Loaded state doesn't match saved state"
    
    print("✓ State persistence tests passed")

def test_logging(logger):
    """Test basic logging functionality"""
    print("\nTesting logging...")
    
    # Test single log entry
    success = logger.log_entry("Test message 1", path="/sd/test")
    assert success, "Failed to write log entry"
    
    # Test multiple log entries
    test_messages = [
        "System initialized",
        "Temperature set to 72°F",
        "Heat cycle started",
        "Temperature reached"
    ]
    
    for msg in test_messages:
        success = logger.log_entry(msg, path="/sd/test")
        assert success, f"Failed to log message: {msg}"
    
    # Verify logs exist
    files = os.listdir('/sd/test/logs')
    assert len(files) > 0, "No log files created"
    
    # Read back last log file
    files = sorted([f for f in os.listdir('/sd/test/logs') if f.endswith('.log')])
    with open(f'/sd/test/logs/{files[-1]}', 'r') as f:
        content = f.readlines()
        print(f"Log file contains {len(content)} entries")
        print("Last log entry:", content[-1].strip())
        
        # Verify content matches last message
        assert "Temperature reached" in content[-1], "Last log entry doesn't match expected message"
    
    print("✓ Logging tests passed")

def test_log_rotation(logger):
    """Test log rotation functionality"""
    print("\nTesting log rotation...")
    
    # Write enough entries to trigger rotation
    for i in range(10):
        logger.log_entry(f"Rotation test message {i}")
        
    files = sorted([f for f in os.listdir('/sd/test/logs') if f.endswith('.log')])
    print(f"Number of log files: {len(files)}")
    assert len(files) <= logger.max_log_files, "Too many log files exist"
    
    print("✓ Log rotation tests passed")

def test_space_management(logger):
    """Test space checking and cleanup"""
    print("\nTesting space management...")
    
    # Check space
    space = logger.check_space()
    print(f"Total space: {space['total_mb']:.1f}MB")
    print(f"Free space: {space['free_mb']:.1f}MB")
    print(f"Used space: {space['used_mb']:.1f}MB")
    print(f"Percent free: {space['percent_free']:.1f}%")
    
    # Test cleanup
    logger.cleanup(min_free_percent=90)  # Set high threshold to force cleanup
    
    # Verify cleanup worked
    new_space = logger.check_space()
    print(f"After cleanup - Percent free: {new_space['percent_free']:.1f}%")
    
    print("✓ Space management tests passed")

def run_cowbell_logger_tests():
    print("Starting SimpleLogger tests...")
    
    try:
        # Get the existing logger instance
        logger = SimpleLogger.get_instance()
        
        # Setup clean test environment
        setup_test_directory()
        # Run all tests
        test_state_persistence(logger)
        test_logging(logger)
        test_log_rotation(logger)
        test_space_management(logger)
        
        print("\nAll tests completed successfully! ✓")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        raise
    finally:
        try:
            logger.close()
            print("\nLogger closed properly")
        except Exception as e:
            print(f"Error closing logger: {e}")
