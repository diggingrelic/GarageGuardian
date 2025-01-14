"""
Test suite for PCF8523 RTC library
"""
from gg.testing.hardware_tests.pcf8523_test import PCF8523, PCF8523Error
import time

def run_tests():
    print("Starting PCF8523 RTC tests...")
    
    try:
        # Initialize RTC
        rtc = PCF8523()  # Using default pins (GP4/GP5)
        print("✓ RTC initialization successful")
        
        # Test setting date/time
        print("\nTesting set_datetime...")
        test_date = (2024, 1, 11, 4, 13, 30, 0)  # Year, Month, Day, Weekday, Hours, Minutes, Seconds
        rtc.set_datetime(*test_date)
        print("✓ Set datetime successful")
        
        # Wait a moment for RTC to update
        time.sleep(1)
        
        # Test reading functions
        print("\nTesting reading functions...")
        
        # Test get_datetime
        dt = rtc.get_datetime()
        print(f"DateTime: {dt}")
        assert dt['year'] == test_date[0], "Year mismatch"
        assert dt['month'] == test_date[1], "Month mismatch"
        assert dt['day'] == test_date[2], "Day mismatch"
        print("✓ get_datetime successful")
        
        # Test get_formatted_datetime
        formatted = rtc.get_formatted_datetime()
        print(f"Formatted DateTime: {formatted}")
        assert len(formatted) == 19, "Formatted datetime length incorrect"
        print("✓ get_formatted_datetime successful")
        
        # Test get_date
        year, month, day = rtc.get_date()
        print(f"Date: {year}-{month:02d}-{day:02d}")
        assert year == test_date[0], "Year mismatch in get_date"
        print("✓ get_date successful")
        
        # Test get_time
        hours, minutes, seconds = rtc.get_time()
        print(f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print("✓ get_time successful")
        
        # Test get_weekday and get_weekday_name
        weekday = rtc.get_weekday()
        weekday_name = rtc.get_weekday_name()
        print(f"Weekday: {weekday} ({weekday_name})")
        assert 1 <= weekday <= 7, "Invalid weekday number"
        assert weekday_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        print("✓ get_weekday functions successful")
        
        # Test get_unix_time
        unix_time = rtc.get_unix_time()
        print(f"Unix Time: {unix_time}")
        assert unix_time > 1704067200  # Jan 1, 2024
        print("✓ get_unix_time successful")
        
        print("\nAll tests passed successfully! ✓")
        
    except AssertionError as e:
        print(f"Test failed: {str(e)} ✗")
    except PCF8523Error as e:
        print(f"RTC error: {str(e)} ✗")
    except Exception as e:
        print(f"Unexpected error: {str(e)} ✗")

if __name__ == "__main__":
    run_tests()