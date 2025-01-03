# MicroPython IoT Controller

A robust, event-driven IoT controller system designed for MicroPython-enabled devices. This project provides a framework for managing IoT devices with a focus on safety, reliability, and extensibility.

## Features

- Event-driven architecture
- Safety monitoring system
- Rule-based automation
- Hardware abstraction layer
- Custom testing framework
- Memory-efficient design
- Async support

## Project Structure 

gg/
├── core/
│ ├── Events.py # Event system
│ ├── Rules.py # Rules engine
│ └── Safety.py # Safety monitoring
├── controllers/
│ ├── Base.py # Base controller
│ └── Door.py # Door controller
├── hardware/
│ ├── Interfaces.py # Hardware interfaces
│ └── MockHAL.py # Mock hardware for testing
├── testing/
│ ├── microtest.py # Testing framework
│ ├── mocks.py # Mock objects
│ └── tests/ # Test files
├── IoTController.py # Main controller
└── init.py

## Installation

1. Clone the repository:
2. Install dependencies:
    - `MicroPython v1.24.1` https://micropython.org/download/RPI_PICO_W/
    - `micropython-logging` https://github.com/micropython/micropython-lib/tree/master/logging
    - `mpremote` https://github.com/micropython/micropython/tree/master/tools/mpremote
3. Install on Raspberry Pi Pico W:
    - `mpremote fs cp -r * :.`
4. Run tests:
    Set config.py DEBUG to True
    Set config.py RUN_TESTS to True
    Set config.py LOG_LEVEL to DEBUG
    Connect to Raspberry Pi Pico W via USB and run main.py `mpremote run main.py`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT - See LICENSE file for details

## Authors

Brandon Bearden
