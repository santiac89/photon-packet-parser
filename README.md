# photon-packet-parser

The `photon-packet-parser` is a Python library designed to parse and analyze packets transmitted using the [Photon Protocol16](https://doc.photonengine.com/) based on the C# library coded by [0blu](https://github.com/0blu/PhotonPackageParser). This library provides developers with a convenient way to decode and inspect Photon Protocol packets in their Python applications.

## Warning
This library is incomplete as I merely needed some parts of it for my own project. I will add more features as I need them. It is not fully tested and far from being used in a production environment. If you need a feature that is not implemented yet, feel free to open an issue or submit a pull request.

## Features

- Parsing and decoding of Photon Protocol packets
- Callbacks for handling different packet actions
- Access to packet headers, payload, and metadata

## Installation

You can install the `photon-packet-parser` library using pip:

```bash
pip install photon-packet-parser
```

## Usage
To use the library, start by importing the PhotonPacketParser class:

```python
from photon_packet_parser import PhotonPacketParser
```

Then, create an instance of the PhotonPacketParser class and provide the necessary callbacks:

```python
def on_event(header, payload):
    # Callback for handling event packets
    pass

def on_request(header, payload):
    # Callback for handling request packets
    pass

def on_response(header, payload):
    # Callback for handling response packets
    pass

parser = PhotonPacketParser(on_event, on_request, on_response)
```

Once the parser object is created, you can use the handle_payload method to parse a payload:

```python
payload_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
parser.handle_payload(payload_data)
```

The library will invoke the appropriate callback based on the packet type encountered during parsing.

For more advanced usage and customization options, please refer to the documentation.

# Examples

## Parsing a Photon Protocol packet
```python
from photon_packet_parser import PhotonPacketParser

def on_event(header, payload):
    # Handle event packets
    print("Received event packet")

def on_request(header, payload):
    # Handle request packets
    print("Received request packet")

def on_response(header, payload):
    # Handle response packets
    print("Received response packet")

# Create a parser instance with callbacks
parser = PhotonPacketParser(on_event, on_request, on_response)

# Parse a payload
payload_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
parser.handle_payload(payload_data)
```

# Contributing
Contributions to the photon-packet-parser library are welcome! If you find any bugs, have feature requests, or want to contribute improvements, please open an issue or submit a pull request on the GitHub repository.

When contributing, please follow the existing code style and ensure that all tests pass before submitting your changes.

# License
The photon-packet-parser library is licensed under the MIT License. You are free to use, modify, and distribute this library in accordance with the terms of the license.

# Acknowledgements

This library was inspired by [0blu](https://github.com/0blu/PhotonPackageParser) implementation and the need for a Python parser. 