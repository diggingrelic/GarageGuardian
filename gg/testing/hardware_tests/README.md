# Hardware Integration Tests

These tests are designed to verify physical hardware functionality and require manual verification.

## Running Tests

```

## Test Categories

### Relay Tests
- Verify physical relay activation
- Check for proper clicking sound
- Confirm LED indicators (if present)
- Validate timing of switching operations

### Temperature Sensor Tests
- Verify I2C communication
- Validate temperature readings
- Check update frequency
- Monitor sensor reliability

## Safety Notes
1. Never run tests with live AC power connected
2. Allow proper delays between relay operations
3. Monitor relay temperature during extended testing
4. Document any unusual behavior
