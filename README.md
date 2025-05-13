# FCB1010 Editor

A Python library for interfacing with the Behringer FCB1010 MIDI foot controller. This library allows you to read, write, and edit presets for the FCB1010, as well as to control it via MIDI messages.

## Features

- Connect to FCB1010 via MIDI
- Send and receive MIDI messages
- Read and write presets
- Edit presets programmatically
- Google Sheets integration for easy preset editing

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fcb1010-editor.git
cd fcb1010-editor

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from fcb1010 import FCB1010, Preset

# Connect to FCB1010
fcb = FCB1010()

# Send a program change message
fcb.send_program_change(10)

# Send a control change message
fcb.send_control_change(7, 127)  # Set volume to max

# Close the connection
fcb.close()
```

### Working with Presets

```python
# Create a new preset
preset = Preset(5, "My Awesome Preset")

# Add program and control changes
preset.add_program_change(10, channel=0)
preset.add_control_change(7, 127, channel=0)  # Volume
preset.add_control_change(10, 64, channel=0)  # Pan

# Convert to dictionary for saving
preset_data = preset.to_dict()

# Create from dictionary
loaded_preset = Preset.from_dict(preset_data)
```

### Example Scripts

Check out the `scripts` directory for example usage:

```bash
# Run the example script
python scripts/example_usage.py
```

## Testing

To run the tests:

```bash
python -m unittest discover tests
```

## Requirements

- Python 3.6+
- rtmidi
- gspread (for Google Sheets integration)
- oauth2client (for Google Sheets authentication)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.