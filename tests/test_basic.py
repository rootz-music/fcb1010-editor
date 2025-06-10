# Sample test for FCB1010 Editor
import unittest
from src.fcb1010 import Preset

class TestPreset(unittest.TestCase):
    def test_preset_creation(self):
        preset = Preset(1, "Test Preset")
        self.assertEqual(preset.preset_number, 1)
        self.assertEqual(preset.name, "Test Preset")
        self.assertEqual(preset.program_changes, [])
        self.assertEqual(preset.control_changes, [])

if __name__ == "__main__":
    unittest.main()
