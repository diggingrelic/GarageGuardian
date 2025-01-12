"""
PCF8523 Real Time Clock Library for Raspberry Pi Pico
Provides high-level interface for the PCF8523 RTC on PiCowbell Adalogger
"""
from machine import I2C, Pin
import time

class PCF8523Error(Exception):
    """Custom exception for PCF8523 errors"""
    pass

class PCF8523:
    # Register addresses
    CONTROL_1 = 0x00
    CONTROL_2 = 0x01
    CONTROL_3 = 0x02
    SECONDS = 0x03
    MINUTES = 0x04
    HOURS = 0x05
    DAYS = 0x06
    WEEKDAYS = 0x07
    MONTHS = 0x08
    YEARS = 0x09
    
    def __init__(self, sda_pin=4, scl_pin=5, i2c_id=0):
        """Initialize the PCF8523 RTC.
        
        Args:
            sda_pin (int): GPIO pin number for SDA
            scl_pin (int): GPIO pin number for SCL
            i2c_id (int): I2C bus ID (0 or 1)
        
        Raises:
            PCF8523Error: If device not found or initialization fails
        """
        self.addr = 0x68
        self.i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100000)
        
        if self.addr not in self.i2c.scan():
            raise PCF8523Error(f"PCF8523 not found at address {hex(self.addr)}")
        
        # Initialize RTC
        try:
            self.i2c.writeto_mem(self.addr, self.CONTROL_1, b'\x00')
            self.i2c.writeto_mem(self.addr, self.CONTROL_2, b'\x00')
            self.i2c.writeto_mem(self.addr, self.CONTROL_3, b'\x00')
        except Exception as e:
            raise PCF8523Error(f"Failed to initialize RTC: {str(e)}")
    
    def _bcd2dec(self, bcd):
        """Convert BCD to decimal."""
        return (((bcd & 0x70) >> 4) * 10 + (bcd & 0x0F))
    
    def _dec2bcd(self, dec):
        """Convert decimal to BCD."""
        tens, units = divmod(dec, 10)
        return (tens << 4) + units
    
    def get_datetime(self):
        """Get the current date and time as a dictionary.
        
        Returns:
            dict: Contains year, month, day, weekday, hours, minutes, seconds
            
        Raises:
            PCF8523Error: If reading fails
        """
        try:
            data = self.i2c.readfrom_mem(self.addr, self.SECONDS, 7)
            
            return {
                'year': self._bcd2dec(data[6]) + 2000,
                'month': self._bcd2dec(data[5] & 0x1F),
                'day': self._bcd2dec(data[3] & 0x3F),
                'weekday': data[4] & 0x07,
                'hours': self._bcd2dec(data[2] & 0x3F),
                'minutes': self._bcd2dec(data[1] & 0x7F),
                'seconds': self._bcd2dec(data[0] & 0x7F)
            }
        except Exception as e:
            raise PCF8523Error(f"Failed to read datetime: {str(e)}")
    
    def get_formatted_datetime(self, include_seconds=True):
        """Get formatted date and time string.
        
        Args:
            include_seconds (bool): Whether to include seconds in the output
            
        Returns:
            str: Formatted datetime string (e.g., "2024-01-11 13:45:30")
            
        Raises:
            PCF8523Error: If reading fails
        """
        dt = self.get_datetime()
        if include_seconds:
            return f"{dt['year']}-{dt['month']:02d}-{dt['day']:02d} {dt['hours']:02d}:{dt['minutes']:02d}:{dt['seconds']:02d}"
        return f"{dt['year']}-{dt['month']:02d}-{dt['day']:02d} {dt['hours']:02d}:{dt['minutes']:02d}"
    
    def get_date(self):
        """Get current date components.
        
        Returns:
            tuple: (year, month, day)
            
        Raises:
            PCF8523Error: If reading fails
        """
        dt = self.get_datetime()
        return (dt['year'], dt['month'], dt['day'])
    
    def get_time(self):
        """Get current time components.
        
        Returns:
            tuple: (hours, minutes, seconds)
            
        Raises:
            PCF8523Error: If reading fails
        """
        dt = self.get_datetime()
        return (dt['hours'], dt['minutes'], dt['seconds'])
    
    def get_weekday(self):
        """Get current weekday (1=Monday through 7=Sunday).
        
        Returns:
            int: Day of week (1-7)
            
        Raises:
            PCF8523Error: If reading fails
        """
        return self.get_datetime()['weekday']
    
    def get_weekday_name(self):
        """Get weekday name.
        
        Returns:
            str: Day name (e.g., "Monday")
            
        Raises:
            PCF8523Error: If reading fails
        """
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.get_weekday() - 1]
    
    def get_unix_time(self):
        """Get Unix timestamp (seconds since 1970-01-01 00:00:00 UTC).
        
        Returns:
            int: Unix timestamp
            
        Raises:
            PCF8523Error: If reading fails
        """
        dt = self.get_datetime()
        
        # Basic implementation - doesn't account for timezone or DST
        days = 0
        months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        year = dt['year']
        
        # Days in previous years
        for y in range(1970, year):
            if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0):
                days += 366
            else:
                days += 365
        
        # Days in current year
        for m in range(1, dt['month']):
            days += months[m-1]
            if m == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                days += 1
        
        days += dt['day'] - 1
        
        seconds = days * 86400
        seconds += dt['hours'] * 3600
        seconds += dt['minutes'] * 60
        seconds += dt['seconds']
        
        return seconds
    
    def set_datetime(self, year, month, day, weekday, hours, minutes, seconds):
        """Set the RTC date and time.
        
        Args:
            year (int): Full year (e.g., 2024)
            month (int): Month (1-12)
            day (int): Day (1-31)
            weekday (int): Day of week (1=Monday through 7=Sunday)
            hours (int): Hours (0-23)
            minutes (int): Minutes (0-59)
            seconds (int): Seconds (0-59)
            
        Raises:
            PCF8523Error: If setting time fails
            ValueError: If any values are out of range
        """
        # Input validation
        if not (2000 <= year <= 2099):
            raise ValueError("Year must be between 2000 and 2099")
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        if not (1 <= day <= 31):
            raise ValueError("Day must be between 1 and 31")
        if not (1 <= weekday <= 7):
            raise ValueError("Weekday must be between 1 and 7")
        if not (0 <= hours <= 23):
            raise ValueError("Hours must be between 0 and 23")
        if not (0 <= minutes <= 59):
            raise ValueError("Minutes must be between 0 and 59")
        if not (0 <= seconds <= 59):
            raise ValueError("Seconds must be between 0 and 59")
            
        try:
            data = bytearray(7)
            data[0] = self._dec2bcd(seconds)
            data[1] = self._dec2bcd(minutes)
            data[2] = self._dec2bcd(hours)
            data[3] = self._dec2bcd(day)
            data[4] = weekday & 0x07
            data[5] = self._dec2bcd(month)
            data[6] = self._dec2bcd(year - 2000)
            
            self.i2c.writeto_mem(self.addr, self.SECONDS, data)
        except Exception as e:
            raise PCF8523Error(f"Failed to set datetime: {str(e)}")