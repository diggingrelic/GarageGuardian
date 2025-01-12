'''
# Initialize logger
logger = SimpleLogger()

# Save thermostat state
state = {
    "target_temp": 72,
    "mode": "heat",
    "schedule": {"wake": "6:00", "sleep": "22:00"}
}
logger.save_state(state)

# Log events
logger.log_entry("Temperature changed to 73°F")
logger.log_entry("Heat cycle started")

# Load state after power loss
saved_state = logger.load_state()
if saved_state:
    target_temp = saved_state["target_temp"]
    mode = saved_state["mode"]

# Always close properly
logger.close()
'''


from machine import Pin, SPI # type: ignore
import lib.sdcard as sdcard
import os
import json
from gg.devices.pcf8523 import PCF8523

class SimpleLogger:
    _instance = None
    
    @classmethod
    def get_instance(cls, **kwargs):
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance
    
    @classmethod
    def set_instance(cls, logger):
        """Allow setting a test logger"""
        cls._instance = logger
        
    def __init__(self, max_log_files=7, state_file="/sd/state.json"):
        if SimpleLogger._instance is not None:
            raise RuntimeError("Use get_instance() instead")
        """
        Initialize logger with SD card.
        max_log_files: Number of log files to keep before rotation
        state_file: Name of file to store persistent state
        """
        self.max_log_files = max_log_files
        self.state_file = state_file
        self.rtc = PCF8523()
        self._init_sd()
        
    def _init_sd(self):
        # Initialize SPI for SD card (PiCowbell pins)
        spi = SPI(0,
                  baudrate=100000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=SPI.MSB,
                  sck=Pin(18),
                  mosi=Pin(19),
                  miso=Pin(16))
        
        cs = Pin(17, Pin.OUT)
        self.sd = sdcard.SDCard(spi, cs)
        os.mount(self.sd, '/sd')
        
        # Ensure logs directory exists
        try:
            os.mkdir('/sd/logs')
        except OSError:  # Directory already exists
            pass
    
    def save_state(self, state_data, path=None, state_file=None):
        """Save persistent state data"""
        try:
            # Use provided state_file if given, otherwise use default
            filename = state_file if state_file else self.state_file
            if path:  # If path provided, construct full path
                filename = f"{path}/{filename}"
            with open(filename, 'w') as f:
                json.dump(state_data, f)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self, path=None, state_file=None):
        """Load persistent state data"""
        try:
            # Use provided state_file if given, otherwise use default
            filename = state_file if state_file else self.state_file
            if path:  # If path provided, construct full path
                filename = f"{path}/{filename}"
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    def log_entry(self, message, path="/sd"):
        """Log a message with timestamp"""
        try:
            # Get current date for filename
            date = self.rtc.get_formatted_datetime().split()[0]
            filename = f"{date}.log"
            
            # Create log entry with timestamp
            timestamp = self.rtc.get_formatted_datetime()
            entry = f"{timestamp}: {message}\n"
            
            # Write to log file
            with open(f'{path}/logs/{filename}', 'a') as f:
                f.write(entry)
            
            # Check if we need to rotate logs
            self._rotate_logs()
            return True
        except Exception as e:
            print(f"Error logging entry: {e}")
            return False
    
    def _rotate_logs(self):
        """Remove old log files if we exceed max_log_files"""
        try:
            # Get list of log files
            log_files = sorted([f for f in os.listdir('/sd/logs') if f.endswith('.log')])
            
            # Remove oldest files if we have too many
            while len(log_files) > self.max_log_files:
                oldest = log_files.pop(0)
                os.remove(f'/sd/logs/{oldest}')
        except Exception as e:
            print(f"Error rotating logs: {e}")
    
    def check_space(self):
        """Check available space on SD card"""
        stats = os.statvfs('/sd')
        block_size = stats[0]
        total_blocks = stats[2]
        free_blocks = stats[3]
        
        total_size = block_size * total_blocks / 1024 / 1024  # MB
        free_size = block_size * free_blocks / 1024 / 1024    # MB
        
        return {
            'total_mb': total_size,
            'free_mb': free_size,
            'used_mb': total_size - free_size,
            'percent_free': (free_blocks / total_blocks) * 100
        }
    
    def cleanup(self, min_free_percent=10):
        """Remove old logs if space is low"""
        space = self.check_space()
        if space['percent_free'] < min_free_percent:
            log_files = sorted([f for f in os.listdir('/sd/logs') if f.endswith('.log')])
            # Remove oldest half of log files
            for f in log_files[:len(log_files)//2]:
                os.remove(f'/sd/logs/{f}')
    
    def close(self):
        """Safely unmount SD card"""
        try:
            os.umount('/sd')
        except Exception as e:
            print(f"Error unmounting SD card: {e}")
    
    def delete_state(self, path=None, state_file=None):
        """Delete a state file"""
        try:
            # Use provided state_file if given, otherwise use default
            filename = state_file if state_file else self.state_file
            if path:  # If path provided, construct full path
                filename = f"{path}/{filename}"
            os.remove(filename)
            return True
        except Exception as e:
            print(f"Error deleting state file: {e}")
            return False