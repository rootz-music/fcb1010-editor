"""
FCB1010 Editor - A Python library for interfacing with the Behringer FCB1010 MIDI foot controller.

This module provides classes and functions to read, write, and edit presets for the FCB1010 midi foot controller.
"""

import rtmidi
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FCB1010:
    """
    Main class for interfacing with the Behringer FCB1010 MIDI foot controller.
    """

    def __init__(self, input_port=None, output_port=None):
        """
        Initialize the FCB1010 interface.

        Args:
            input_port (int, optional): MIDI input port index. If not provided, the first available port is used.
            output_port (int, optional): MIDI output port index. If not provided, the first available port is used.
        """
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        # Get available ports
        available_in_ports = self.midi_in.get_ports()
        available_out_ports = self.midi_out.get_ports()

        logger.info(f"Available MIDI Input ports: {available_in_ports}")
        logger.info(f"Available MIDI Output ports: {available_out_ports}")

        # Connect to MIDI ports
        if input_port is not None and 0 <= input_port < len(available_in_ports):
            self.midi_in.open_port(input_port)
            logger.info(
                f"Connected to MIDI Input port: {available_in_ports[input_port]}"
            )
        elif available_in_ports:
            # Find a port containing "FCB1010" if possible
            fcb_ports = [
                i for i, port in enumerate(available_in_ports) if "FCB1010" in port
            ]
            if fcb_ports:
                self.midi_in.open_port(fcb_ports[0])
                logger.info(
                    f"Connected to FCB1010 MIDI Input port: {available_in_ports[fcb_ports[0]]}"
                )
            else:
                self.midi_in.open_port(0)
                logger.info(
                    f"Connected to default MIDI Input port: {available_in_ports[0]}"
                )
        else:
            logger.warning("No MIDI Input ports available. Creating virtual port.")
            self.midi_in.open_virtual_port("FCB1010 Input")

        # Set up MIDI output port similarly
        if output_port is not None and 0 <= output_port < len(available_out_ports):
            self.midi_out.open_port(output_port)
            logger.info(
                f"Connected to MIDI Output port: {available_out_ports[output_port]}"
            )
        elif available_out_ports:
            fcb_ports = [
                i for i, port in enumerate(available_out_ports) if "FCB1010" in port
            ]
            if fcb_ports:
                self.midi_out.open_port(fcb_ports[0])
                logger.info(
                    f"Connected to FCB1010 MIDI Output port: {available_out_ports[fcb_ports[0]]}"
                )
            else:
                self.midi_out.open_port(0)
                logger.info(
                    f"Connected to default MIDI Output port: {available_out_ports[0]}"
                )
        else:
            logger.warning("No MIDI Output ports available. Creating virtual port.")
            self.midi_out.open_virtual_port("FCB1010 Output")

        # Set up a callback function for incoming MIDI messages
        self.midi_in.set_callback(self._midi_callback)

        # Current preset
        self.current_preset = None

    def _midi_callback(self, message, time_stamp):
        """
        Callback function for MIDI messages.

        Args:
            message (tuple): MIDI message data
            time_stamp (float): Timestamp of the message
        """
        logger.debug(f"MIDI message received: {message} at {time_stamp}")
        # Process MIDI message here
        if len(message) > 0:
            status = message[0][0] & 0xF0  # Extract status byte
            if status == 0xC0:  # Program Change
                preset_num = message[0][1]
                logger.info(f"Program Change: Preset {preset_num}")
                self.current_preset = preset_num

    def send_program_change(self, program_number, channel=0):
        """
        Send a Program Change message to the FCB1010.

        Args:
            program_number (int): The program number (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        if 0 <= program_number <= 127 and 0 <= channel <= 15:
            status = 0xC0 | channel  # Program Change status byte
            message = [status, program_number]
            self.midi_out.send_message(message)
            logger.info(f"Sent Program Change: {program_number} on channel {channel}")
        else:
            logger.error(
                f"Invalid program number ({program_number}) or channel ({channel})"
            )

    def send_control_change(self, controller, value, channel=0):
        """
        Send a Control Change message to the FCB1010.

        Args:
            controller (int): Controller number (0-127)
            value (int): Controller value (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        if 0 <= controller <= 127 and 0 <= value <= 127 and 0 <= channel <= 15:
            status = 0xB0 | channel  # Control Change status byte
            message = [status, controller, value]
            self.midi_out.send_message(message)
            logger.info(
                f"Sent Control Change: controller={controller}, value={value}, channel={channel}"
            )
        else:
            logger.error(
                f"Invalid controller ({controller}), value ({value}), or channel ({channel})"
            )

    def read_preset(self, preset_number):
        """
        Read preset data from the FCB1010.

        Args:
            preset_number (int): The preset number to read (0-99)

        Returns:
            dict: Preset data or None if read failed
        """
        # This would require implementation of MIDI SysEx messages for FCB1010
        # The actual implementation depends on the FCB1010 SysEx specification
        logger.info(f"Reading preset {preset_number}")
        # Placeholder - actual implementation would send SysEx requests and process responses
        return {"preset_number": preset_number, "name": f"Preset {preset_number}"}

    def write_preset(self, preset_data):
        """
        Write preset data to the FCB1010.

        Args:
            preset_data (dict): Preset data to write

        Returns:
            bool: True if successful, False otherwise
        """
        # This would require implementation of MIDI SysEx messages for FCB1010
        preset_number = preset_data.get("preset_number")
        logger.info(f"Writing preset {preset_number}")
        # Placeholder - actual implementation would format data and send SysEx messages
        return True

    def close(self):
        """
        Close MIDI connections.
        """
        if self.midi_in:
            self.midi_in.close_port()
        if self.midi_out:
            self.midi_out.close_port()
        logger.info("Closed MIDI connections")


class Preset:
    """
    Class representing an FCB1010 preset.
    """

    def __init__(self, preset_number, name=""):
        """
        Initialize a new preset.

        Args:
            preset_number (int): Preset number (0-99)
            name (str, optional): Preset name. Defaults to "".
        """
        self.preset_number = preset_number
        self.name = name if name else f"Preset {preset_number}"
        self.program_changes = []
        self.control_changes = []

    def add_program_change(self, program_number, channel=0):
        """
        Add a program change message to this preset.

        Args:
            program_number (int): Program number (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        self.program_changes.append({"program": program_number, "channel": channel})

    def add_control_change(self, controller, value, channel=0):
        """
        Add a control change message to this preset.

        Args:
            controller (int): Controller number (0-127)
            value (int): Controller value (0-127)
            channel (int, optional): MIDI channel (0-15). Defaults to 0.
        """
        self.control_changes.append(
            {"controller": controller, "value": value, "channel": channel}
        )

    def to_dict(self):
        """
        Convert preset to dictionary.

        Returns:
            dict: Preset data as dictionary
        """
        return {
            "preset_number": self.preset_number,
            "name": self.name,
            "program_changes": self.program_changes,
            "control_changes": self.control_changes,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a Preset object from dictionary data.

        Args:
            data (dict): Preset data

        Returns:
            Preset: New Preset object
        """
        preset = cls(data["preset_number"], data.get("name", ""))

        for pc in data.get("program_changes", []):
            preset.add_program_change(pc["program"], pc.get("channel", 0))

        for cc in data.get("control_changes", []):
            preset.add_control_change(
                cc["controller"], cc["value"], cc.get("channel", 0)
            )

        return preset
