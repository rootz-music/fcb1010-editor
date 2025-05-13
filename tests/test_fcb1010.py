#!/usr/bin/env python3
"""
Tests for the FCB1010 library.
"""

import unittest
import sys
from pathlib import Path
import json

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fcb1010 import FCB1010, Preset

class TestPreset(unittest.TestCase):
    """Test cases for the Preset class"""
    
    def test_preset_initialization(self):
        """Test preset initialization"""
        preset = Preset(10, "Test Preset")
        self.assertEqual(preset.preset_number, 10)
        self.assertEqual(preset.name, "Test Preset")
        self.assertEqual(preset.program_changes, [])
        self.assertEqual(preset.control_changes, [])
        
    def test_preset_default_name(self):
        """Test preset default name generation"""
        preset = Preset(5)
        self.assertEqual(preset.name, "Preset 5")
        
    def test_add_program_change(self):
        """Test adding program changes to preset"""
        preset = Preset(1)
        preset.add_program_change(42, 2)
        
        self.assertEqual(len(preset.program_changes), 1)
        self.assertEqual(preset.program_changes[0]["program"], 42)
        self.assertEqual(preset.program_changes[0]["channel"], 2)
        
    def test_add_control_change(self):
        """Test adding control changes to preset"""
        preset = Preset(1)
        preset.add_control_change(7, 100, 3)
        
        self.assertEqual(len(preset.control_changes), 1)
        self.assertEqual(preset.control_changes[0]["controller"], 7)
        self.assertEqual(preset.control_changes[0]["value"], 100)
        self.assertEqual(preset.control_changes[0]["channel"], 3)
        
    def test_to_dict(self):
        """Test converting preset to dictionary"""
        preset = Preset(7, "My Preset")
        preset.add_program_change(10, 0)
        preset.add_control_change(7, 127, 1)
        
        data = preset.to_dict()
        
        self.assertEqual(data["preset_number"], 7)
        self.assertEqual(data["name"], "My Preset")
        self.assertEqual(len(data["program_changes"]), 1)
        self.assertEqual(len(data["control_changes"]), 1)
        
    def test_from_dict(self):
        """Test creating preset from dictionary"""
        data = {
            "preset_number": 5,
            "name": "From Dict Test",
            "program_changes": [
                {"program": 20, "channel": 1},
                {"program": 30}  # Test default channel
            ],
            "control_changes": [
                {"controller": 10, "value": 64, "channel": 2},
                {"controller": 11, "value": 127}  # Test default channel
            ]
        }
        
        preset = Preset.from_dict(data)
        
        self.assertEqual(preset.preset_number, 5)
        self.assertEqual(preset.name, "From Dict Test")
        self.assertEqual(len(preset.program_changes), 2)
        self.assertEqual(preset.program_changes[0]["channel"], 1)
        self.assertEqual(preset.program_changes[1]["channel"], 0)  # Default channel
        self.assertEqual(len(preset.control_changes), 2)
        self.assertEqual(preset.control_changes[0]["channel"], 2)
        self.assertEqual(preset.control_changes[1]["channel"], 0)  # Default channel

# We don't directly test the FCB1010 class as it depends on MIDI hardware
# In a real project, you would use mocking to test this class

if __name__ == "__main__":
    unittest.main()