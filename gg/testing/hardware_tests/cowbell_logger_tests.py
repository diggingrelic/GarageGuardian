import os
from gg.logging.cowbell_logger import SimpleLogger
import json

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
    
    success = logger.save_state(test_state, path="/sd/test")
    print(f"Save state successful: {success}")
    assert success, "Failed to save state"
    
    # Test loading state
    loaded_state = logger.load_state(path="/sd/test")
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
        # Initialize logger with test settings
        logger = SimpleLogger(max_log_files=3)
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

class ThermostatStateManager:
    STATE_VERSION = 1
    DEFAULT_STATE = {
        'version': STATE_VERSION,
        'mode': 'off',          
        'target_temp': 72,      
        'schedule_enabled': False,
        'schedule': {
            'wake': {'time': '6:00', 'temp': 72},
            'sleep': {'time': '22:00', 'temp': 65}
        }
    }
    
    def __init__(self, logger):
        self.logger = logger
        self.state_file = '/sd/state/thermostat.json'
        self.state = self._load_state()
        
    def _load_state(self):
        """Load state from file or return defaults if missing/invalid"""
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                
            # Version check
            if state.get('version', 0) != self.STATE_VERSION:
                self.logger.log_entry(f"State version mismatch: {state.get('version')} != {self.STATE_VERSION}")
                raise ValueError("Version mismatch")
                
            return state
            
        except (OSError, ValueError, json.JSONDecodeError) as e:
            self.logger.log_entry(f"Error loading state, using defaults: {str(e)}")
            if isinstance(e, (ValueError, json.JSONDecodeError)):
                # Remove corrupted file
                try:
                    os.remove(self.state_file)
                except OSError:
                    pass
            return self.DEFAULT_STATE.copy()
            
    def save_state(self):
        """Save current state"""
        try:
            # Ensure state directory exists
            try:
                os.mkdir('/sd/state')
            except OSError:
                pass  # Directory exists
                
            # Write state to temp file first
            temp_file = f"{self.state_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.state, f)
                
            # Rename temp file to actual state file
            os.rename(temp_file, self.state_file)
            
            self.logger.log_entry(f"State saved: {self.state['mode']}, {self.state['target_temp']}°F")
            return True
            
        except Exception as e:
            self.logger.log_entry(f"Error saving state: {str(e)}")
            return False
            
    def update(self, key, value):
        """Update state and save immediately"""
        if key in self.DEFAULT_STATE:
            old_value = self.state.get(key)
            self.state[key] = value
            if self.save_state():
                self.logger.log_entry(f"State updated: {key} changed from {old_value} to {value}")
                return True
        return False