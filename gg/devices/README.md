# Final Consolidated Parts List

## Adafruit Components
1. Environmental Sensors
   * 2× SCD-40 CO2 Sensor [ADA4632] - $49.95 each
   * 2× PMSA003I Air Quality Sensor [ADA4632] - $44.95 each
   * 1× BME688 Environmental Sensor [ADA4867] - $19.95

## DigiKey Components

### Core Sensors
1. Temperature/Humidity
   * 2× Sensirion SHT31-DIS [1649-1011-1-ND] - $14.95 each
   * 2× DS18B20 Waterproof [1578-1361-ND] - $9.95 each

2. Precipitation/Ice
   * 1× Hydreon RG-11 Rain Sensor [RG-11-ND] - $49.95

### Security Components
1. Door Monitoring
   * 4× Magnasphere MSS-54SL-W [725-1107-ND] - $15.95 each
   * 1× MCP23017 I/O Expander [MCP23017-E/SP-ND] - $2.95
   * 1× RFID Reader Module [28680-ND] - $29.95
   * 5× RFID Tags [28681-ND] - $2.95 each

2. Alarm
Seco-Larm SH-816S-SQ/R - $60
https://www.amazon.com/Seco-Larm-Self-Contained-Warble-Tone-Broadcasting-Weatherproof/dp/B07XH6GDLC

### Power Control Components
1. Relays
   * 1× 40A SSR (Dust Collector) [CC1140-ND] - $34.95
   * 3× 25A SSR (Heat Tape/Fans) [CC1125-ND] - $24.95 each
   * 1× Power Contactor [PDB11-40-ND] - $34.95

2. Current Monitoring
   * 1× SCT-013-050 50A CT [2258-SCT-013-050-ND] - $24.95
   * 1× SCT-013-030 30A CT [2258-SCT-013-030-ND] - $19.95
   * 2× Current Sensing Kit [2258-013-CBK-ND] - $4.95 each
   * 1× ADS1115 ADC [296-24934-1-ND] - $12.95

### Control Interface
1. Main Components
   * 1× Raspberry Pi Zero W [RASPBERRY-PI-ZERO-W] - $14.00
   * 1× 3.5" Touch Display [2302-LCD-35-ND] - $34.95
   * 1× 32GB MicroSD [AF3932-ND] - $12.95
   * 1× DS3231 RTC [1528-1778-ND] - $9.95

### Interface Components
1. Level Shifters/Connectors
   * 2× TXS0108E Level Shifter [296-27573-1-ND] - $2.95 each
   * 1× Emergency Stop Button [1948-1056-ND] - $14.95

### Supporting Components
1. Power Supply
   * 1× 12V 2A Supply [1470-3186-ND] - $12.95
   * 1× 5V 2.5A Supply [1866-2578-ND] - $8.95
   * 1× 12V 2.3Ah Battery [312-1241-ND] - $19.95

2. Protection
   * 4× MOV Surge Protector [495-2049-ND] - $1.95 each
   * 4× Fuse Holder [F9604-ND] - $1.95 each
   * 1× Fuse Kit [F2585-KIT-ND] - $4.95
   * 1× Circuit Breaker [FB3-ND] - $12.95

3. Miscellaneous
   * 2× Terminal Block Set [ED2946-ND] - $3.95 each
   * 1× Resistor Kit [RS-KIT25CR-ND] - $2.95
   * 1× LED Kit (12× RGB) [516-1750-1-ND] - $5.40
   * 1× Enclosure [HM214-ND] - $24.95

## Cost Summary
* Adafruit Components: $209.75
* DigiKey Core Sensors: $99.75
* DigiKey Security: $127.55
* DigiKey Power Control: $197.55
* DigiKey Interface: $71.85
* DigiKey Supporting: $119.45

Total Project Cost: Approximately $825.90

## Notes
* Some components serve multiple subsystems
* Prices may vary based on quantity discounts
* Consider ordering spares of critical components
* Some parts may be available cheaper from alternative sources
* Additional wiring/mounting hardware may be needed





# Environmental Monitoring System Core Components

## Control Center (Indoor Primary)
1. Core Sensor Package
   - Adafruit SCD-40 CO2 Sensor [ADA4632] - $49.95
     * I2C interface
     * CO2, temperature, humidity
   - Adafruit PMSA003I Air Quality Sensor [ADA4632] - $44.95
     * I2C interface
     * PM1.0, PM2.5, PM10 particulate matter

## Outdoor Environment Station
1. Primary Sensor Package
   - BME688 4-in-1 Environmental Sensor [ADA4867] - $19.95
     * Temperature, humidity, pressure, gas
     * I2C interface
   - Adafruit SCD-40 CO2 Sensor [ADA4632] - $49.95
   - Adafruit PMSA003I Air Quality Sensor [ADA4632] - $44.95

## Additional Zone Sensors (×2)
1. Temperature/Humidity Sensors
   - DHT22/AM2302 Digital Sensors [ADA385] - $10.00 each
     * Digital single-wire interface
     * 2 units needed

## Interface Components
1. Level Shifters
   - BSS138 Logic Level Converter [ADA757] - $4.95
     * 2 units recommended for multiple I2C buses

## Parts Summary
1. From Adafruit:
   - 2× SCD-40 CO2 Sensor [ADA4632] = $99.90
   - 2× PMSA003I Air Quality [ADA4632] = $89.90
   - 1× BME688 Environmental [ADA4867] = $19.95
   - 2× DHT22 Temperature/Humidity [ADA385] = $20.00
   - 2× Logic Level Converter [ADA757] = $9.90

Total Adafruit Components: $239.65

Would you like me to locate equivalent DigiKey part numbers for any of these components, or should we move on to detailing another subsystem?


# Environmental Monitoring System Components - DigiKey Options

## Core Sensors (Keep via Adafruit for library support)
1. SCD-40 CO2 Sensors (2×) [Adafruit ADA4632] - $49.95 each
   * Alternative: Sensirion SCD40-D-R2 [1649-SCD40-D-R2-ND] - $39.00 each
   * Recommendation: Stay with Adafruit for easier implementation

2. PMSA003I Air Quality (2×) [Adafruit ADA4632] - $44.95 each
   * Recommendation: Stay with Adafruit due to I2C conversion board included

3. BME688 Environmental [Adafruit ADA4867] - $19.95
   * Alternative: Bosch BME688 [828-1077-1-ND] - $13.50
   * Recommendation: Stay with Adafruit for included breakout board

## DigiKey Components

1. Temperature/Humidity Sensors (2×)
   * Sensirion SHT31-DIS [1649-1011-1-ND] - $14.95 each
   * Better accuracy than DHT22
   * I2C interface (more reliable than DHT22's one-wire)
   * Includes built-in addressing options

2. Logic Level Shifters (2×)
   * TXS0108E 8-Channel Level Shifter [296-27573-1-ND] - $2.95 each
   * Better than BSS138 for multiple I2C lines
   * Handles up to 8 channels each

3. Supporting Components
   * 4.7kΩ I2C Pull-up Resistors (10×) [CF14JT4K70CT-ND] - $0.10 each
   * 0.1µF Bypass Capacitors (10×) [399-9859-1-ND] - $0.12 each
   * 10-Pin Headers (5×) [S7022-ND] - $0.50 each
   * Terminal Blocks for sensors [277-1247-ND] - $0.75 each

## Cost Comparison
1. Adafruit Components:
   * 2× SCD-40 CO2 = $99.90
   * 2× PMSA003I = $89.90
   * 1× BME688 = $19.95
   Total: $209.75

2. DigiKey Components:
   * 2× SHT31-DIS = $29.90
   * 2× TXS0108E = $5.90
   * Misc Components ≈ $10
   Total: $45.80

Total System Cost: Approximately $255.55

## Notes
* The SHT31-DIS is a significant upgrade from the DHT22
* The TXS0108E level shifter is more suitable for multiple I2C devices
* Consider ordering extra supporting components for repairs/modifications
* All selected components operate on 3.3V logic compatible with Pi Pico W

Would you like me to:
1. Find alternate suppliers for any components?
2. Detail the wiring requirements?
3. Move on to another subsystem?

# Security System Components

## Door Monitoring
1. Contact Sensors
   * 4× Magnasphere MSS-54SL-W [725-1107-ND] - $15.95 each
   * Total: $63.80

2. Input Monitoring
   * MCP23017 16-bit I/O Expander [MCP23017-E/SP-ND] - $2.95
     - Provides interrupt capability
     - I2C interface
     - Handles all contact monitoring
   * 10kΩ Pull-up Resistors (10×) [CF14JT10K0CT-ND] - $0.10 each

3. Status Indicators
   * 4× RGB LED [516-1750-1-ND] - $0.45 each
   * Current limiting resistor kit [RS-KIT25CR-ND] - $2.95

## Alarm Components
1. Audio Alert
   * Piezo Buzzer with built-in driver [668-1443-ND] - $4.95
     - 95dB output
     - 12V operation
   * Logic-level MOSFET [497-2512-5-ND] - $0.75
     - For buzzer control

2. Visual Alert
   * High-brightness Strobe [FM-UC04P-ND] - $8.95
     - 12V operation
     - Weather resistant

## Power Management
1. Main Power
   * 12V 2A Power Supply [1470-3186-ND] - $12.95
   * 3.3V Voltage Regulator [LM3940-3.3-ND] - $2.95
   * Power distribution terminal blocks [277-1247-ND] - $0.75 each (×4)

2. Backup Power
   * 12V 2.3Ah SLA Battery [312-1241-ND] - $19.95
   * Battery charging circuit [MCP73871-2CCI/ML-ND] - $3.95

## Control Interface
1. Arming System
   * RFID Reader Module [28680-ND] - $29.95
     - 13.56MHz
     - I2C interface
   * 5× RFID Tags [28681-ND] - $2.95 each

## Total Component Costs
* Door Sensors: $63.80
* Input Monitoring: $4.95
* Status Indicators: $4.75
* Alarm Components: $14.65
* Power System: $35.95
* Control Interface: $44.70

Total Security System: Approximately $168.80

## Notes
* All components selected for 3.3V/12V operation
* RFID system can be expanded later
* Includes battery backup for power failures
* MCP23017 provides future expansion capability
* Consider adding tamper detection switches to enclosures


# Weather Response System Components

## Snow/Ice Detection
1. Precipitation Detection
   * Hydreon RG-11 Rain Sensor [RG-11-ND] - $49.95
     - Optical rain/snow detection
     - Reliable in cold weather
     - Digital output
     - 12V operation

2. Ice Detection
   * DS18B20 Temperature Sensor (2×) [1578-1361-ND] - $9.95 each
     - One for gutter temperature
     - One for ambient temperature
     - Waterproof version
     - 1-Wire interface
   * 4.7kΩ Pull-up Resistor [CF14JT4K70CT-ND] - $0.10

## Heat Tape Control
1. Power Control
   * 25A Solid State Relay [CC1125-ND] - $24.95
     - 120-240VAC compatible
     - 3.3V control input
     - Zero-crossing switching
   * Heat sink for SSR [HS377-ND] - $4.95
   * Thermal paste [TC002-ND] - $2.95

2. Current Monitoring
   * SCT-013-030 30A Current Transformer [2258-SCT-013-030-ND] - $19.95
     - Non-invasive power monitoring
     - For heat tape current verification
   * Burden resistor and components kit [2258-013-CBK-ND] - $4.95
   * ADC for current sensing:
     - ADS1115 16-bit ADC [296-24934-1-ND] - $12.95
     - I2C interface
     - High precision for power monitoring

3. Protection Components
   * MOV Surge Protector [495-2049-ND] - $1.95
   * Fuse holder [F9604-ND] - $1.95
   * 15A Fuse [F2585-ND] - $0.95
   * Terminal blocks rated for 240V [ED2946-ND] - $3.95 each (×4)

## Status Indicators
1. Visual Feedback
   * High-brightness LED [516-1751-1-ND] - $0.95
   * Current limiting resistor kit [RS-KIT25CR-ND] - $2.95

## Total Component Costs
* Snow/Ice Detection: $69.95
* Power Control: $32.85
* Current Monitoring: $37.85
* Protection Components: $19.65
* Status Indicators: $3.90

Total Weather Response System: Approximately $164.20

## Notes
* System uses existing environmental sensors from previous list
* All high-voltage components UL listed
* Current monitoring provides verification of heat tape operation
* Temperature differential monitoring prevents unnecessary activation
* Consider adding external enclosure for high-voltage components
* System can be expanded to control multiple heat tape zones


# Air Quality Control System Components

## Dust Collection Control
1. Power Control
   * 40A 240V Solid State Relay [CC1140-ND] - $34.95
     - For dust collector motor control
     - Zero-crossing switching
     - Heat sink included
   * Terminal blocks rated for 240V [ED2946-ND] - $3.95 each (×4)

2. Current Monitoring
   * SCT-013-050 50A Current Transformer [2258-SCT-013-050-ND] - $24.95
     - Non-invasive power monitoring
     - Verifies dust collector operation
   * Burden resistor kit [2258-013-CBK-ND] - $4.95
   * Using ADS1115 ADC from weather system

3. Voice Control Interface
   * Microphone Module [1528-4224-ND] - $7.95
     - I2S interface
     - Built-in noise cancellation
   * Audio Amplifier [MAX98357A-ND] - $5.95
   * Small Speaker [668-1492-ND] - $3.95
     - For voice command feedback

## Ventilation Control
1. Garage Door Position Control
   * Using existing door control system
   * Position feedback from security sensors

2. Auxiliary Fan Control
   * 2× 25A Solid State Relay [CC1125-ND] - $24.95 each
     - For controlling ventilation fans
     - 120V compatible
   * 2× Current sensing resistors [SMW3A-ND] - $1.95 each
     - For fan operation verification

## Emergency Shutdown
1. Master Control
   * Emergency stop button [1948-1056-ND] - $14.95
     - Latching mushroom button
     - NC contacts
   * Power contactor [PDB11-40-ND] - $34.95
     - 40A rating
     - 240V coil
     - For complete system shutdown

2. Status Monitoring
   * LED Status Array
     - 4× RGB LED [516-1750-1-ND] - $0.45 each
     - Current limiting resistor kit [RS-KIT25CR-ND] - $2.95
   * Using MCP23017 from security system for I/O

## Protection Components
1. Power Protection
   * Circuit breaker [FB3-ND] - $12.95
   * MOV Surge Protectors (3×) [495-2049-ND] - $1.95 each
   * Fuse holders (3×) [F9604-ND] - $1.95 each
   * Fuse kit [F2585-KIT-ND] - $4.95

## Total Component Costs
* Dust Collection Control: $76.75
* Voice Control: $17.85
* Ventilation Control: $53.80
* Emergency Shutdown: $52.75
* Protection Components: $29.65

Total Air Quality Control System: Approximately $230.80

## Notes
* Uses environmental sensors from previous list for air quality monitoring
* Emergency shutdown system ties into all powered components
* Voice control can be expanded for other functions
* System includes multiple safety verifications
* All high-voltage components UL listed
* Consider adding manual override switches


# Control Systems Components

## Local Interface (Pi Zero W)
1. Core Components
   * Raspberry Pi Zero W [RASPBERRY-PI-ZERO-W] - $14.00
   * MicroSD Card 32GB [AF3932-ND] - $12.95
   * 3.5" Touch Display [2302-LCD-35-ND] - $34.95
     - 480x320 resolution
     - SPI interface
     - Resistive touch

2. Real-Time Clock
   * DS3231 RTC Module [1528-1778-ND] - $9.95
     - Battery backed
     - High accuracy
     - I2C interface
   * CR2032 Battery [P189-ND] - $0.95

3. Power Supply
   * 5V 2.5A Power Supply [1866-2578-ND] - $8.95
   * USB-C connector [2073-USB4085-GF-ACT-ND] - $1.95
   * Power distribution board [1528-2144-ND] - $4.95

## Communication Hub
1. Pico W to Pi Zero Interface
   * Logic Level Converter [296-21929-1-ND] - $2.95
   * 10-pin Header Kit [S7022-ND] - $0.95
   * Ribbon Cable [2273-R40-ND] - $3.95

2. Network Components
   * Ethernet Port (Optional backup) [1568-1926-ND] - $6.95
   * External WiFi Antenna [1568-1927-ND] - $4.95
     - For better range
     - U.FL connector

## Status Display
1. LED Indicators
   * 8× RGB LED [516-1750-1-ND] - $0.45 each
   * LED Driver [MAX7219CNG+-ND] - $7.95
     - SPI interface
     - Handles all indicators
   * Current limiting resistor kit [RS-KIT25CR-ND] - $2.95

## Enclosure Components
1. Main Housing
   * Wall-mount enclosure [HM214-ND] - $24.95
     - Space for display
     - Ventilation
   * Mounting hardware kit [V1032-ND] - $4.95

## Expansion/Debug
1. Development Headers
   * 40-pin Header Strip [S7022-ND] - $1.95
   * Debug Console Port [768-1127-ND] - $5.95
   * Programming jumpers [952-2262-ND] - $2.95

## Total Component Costs
* Local Interface: $71.85
* Communication Hub: $19.75
* Status Display: $15.50
* Enclosure: $29.90
* Expansion: $10.85

Total Control Systems: Approximately $147.85

## Required Software Components
1. Operating System
   * Raspberry Pi OS Lite
   * Custom boot configuration

2. System Software
   * Node.js for web server
   * SQLite for local database
   * Python for main control logic
   * Adafruit IO integration
   * MQTT broker

3. Security Software
   * SSL certificates
   * Authentication system
   * Firewall configuration

## Notes
* Pi Zero W provides WiFi/Bluetooth connectivity
* Real-time clock ensures accurate timing without network
* Display is sunlight readable
* System can operate standalone if network fails
* Consider adding USB port for manual backup/restore
* Plan for future software updates