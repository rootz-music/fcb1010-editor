#!/usr/bin/env python3
"""
Run all tests for the FCB1010 Editor.
"""

import unittest
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __name__ == "__main__":
    unittest.main(module=None, argv=["", "discover", "-s", "tests", "-p", "test_*.py"])
