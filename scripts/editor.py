#!/usr/bin/env python3
"""
FCB1010 Editor - Command Line Interface

This script provides a simple command-line interface for editing FCB1010 presets.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fcb1010 import FCB1010, Preset

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PresetEditor:
    """Command-line interface for editing FCB1010 presets"""
    
    def __init__(self):
        """Initialize the preset editor"""
        self.presets = []
        self.current_file = None
        self.modified = False
        self.fcb = None
        
    def load_presets(self, filename):
        """
        Load presets from a JSON file.
        
        Args:
            filename (str): Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.presets = [Preset.from_dict(p) for p in data]
            self.current_file = filename
            self.modified = False
            logger.info(f"Loaded {len(self.presets)} presets from {filename}")
            return True
        except Exception as e:
            logger.error(f"Error loading presets: {e}")
            return False
            
    def save_presets(self, filename=None):
        """
        Save presets to a JSON file.
        
        Args:
            filename (str, optional): Path to the JSON file. If not provided, uses the current file.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not filename and not self.current_file:
            logger.error("No filename specified")
            return False
            
        target_file = filename or self.current_file
        
        try:
            data = [p.to_dict() for p in self.presets]
            with open(target_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.current_file = target_file
            self.modified = False
            logger.info(f"Saved {len(self.presets)} presets to {target_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving presets: {e}")
            return False
            
    def create_new_preset(self):
        """
        Create a new preset.
        
        Returns:
            Preset: The newly created preset
        """
        # Find the next available preset number
        used_numbers = set(p.preset_number for p in self.presets)
        next_num = 0
        while next_num in used_numbers and next_num < 100:
            next_num += 1
            
        if next_num >= 100:
            logger.warning("All preset numbers (0-99) are already used")
            return None
            
        name = input(f"Enter name for preset {next_num} [Preset {next_num}]: ")
        if not name:
            name = f"Preset {next_num}"
            
        preset = Preset(next_num, name)
        self.presets.append(preset)
        self.modified = True
        logger.info(f"Created new preset: {next_num} - {name}")
        return preset
        
    def edit_preset(self, preset):
        """
        Edit a preset.
        
        Args:
            preset (Preset): The preset to edit
        """
        while True:
            print(f"\nEditing Preset {preset.preset_number}: {preset.name}")
            print("-------------------------------------")
            print(f"1. Change name (current: {preset.name})")
            print("2. Add program change")
            print("3. Add control change")
            print("4. View/edit program changes")
            print("5. View/edit control changes")
            print("6. Done editing")
            
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                name = input(f"Enter new name [{preset.name}]: ")
                if name:
                    preset.name = name
                    self.modified = True
                    
            elif choice == '2':
                try:
                    program = int(input("Enter program number (0-127): "))
                    channel = int(input("Enter channel (0-15) [0]: ") or "0")
                    
                    if 0 <= program <= 127 and 0 <= channel <= 15:
                        preset.add_program_change(program, channel)
                        self.modified = True
                        print(f"Added program change: {program} on channel {channel}")
                    else:
                        print("Invalid values. Program must be 0-127, channel 0-15.")
                except ValueError:
                    print("Please enter valid numbers")
                    
            elif choice == '3':
                try:
                    controller = int(input("Enter controller number (0-127): "))
                    value = int(input("Enter value (0-127): "))
                    channel = int(input("Enter channel (0-15) [0]: ") or "0")
                    
                    if (0 <= controller <= 127 and 0 <= value <= 127 and 0 <= channel <= 15):
                        preset.add_control_change(controller, value, channel)
                        self.modified = True
                        print(f"Added control change: {controller}={value} on channel {channel}")
                    else:
                        print("Invalid values. Controller and value must be 0-127, channel 0-15.")
                except ValueError:
                    print("Please enter valid numbers")
                    
            elif choice == '4':
                self._edit_program_changes(preset)
                
            elif choice == '5':
                self._edit_control_changes(preset)
                
            elif choice == '6':
                break
                
    def _edit_program_changes(self, preset):
        """
        Edit program changes in a preset.
        
        Args:
            preset (Preset): The preset to edit
        """
        while True:
            print("\nProgram Changes")
            print("--------------")
            if not preset.program_changes:
                print("No program changes defined")
            else:
                for i, pc in enumerate(preset.program_changes):
                    print(f"{i+1}. Program: {pc['program']}, Channel: {pc['channel']}")
            
            print("\n1. Add program change")
            if preset.program_changes:
                print("2. Edit program change")
                print("3. Delete program change")
            print("4. Back to preset menu")
            
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                try:
                    program = int(input("Enter program number (0-127): "))
                    channel = int(input("Enter channel (0-15) [0]: ") or "0")
                    
                    if 0 <= program <= 127 and 0 <= channel <= 15:
                        preset.add_program_change(program, channel)
                        self.modified = True
                        print(f"Added program change: {program} on channel {channel}")
                    else:
                        print("Invalid values. Program must be 0-127, channel 0-15.")
                except ValueError:
                    print("Please enter valid numbers")
                    
            elif choice == '2' and preset.program_changes:
                try:
                    idx = int(input(f"Enter index to edit (1-{len(preset.program_changes)}): ")) - 1
                    if 0 <= idx < len(preset.program_changes):
                        pc = preset.program_changes[idx]
                        program = input(f"Enter program number (0-127) [{pc['program']}]: ")
                        channel = input(f"Enter channel (0-15) [{pc['channel']}]: ")
                        
                        if program:
                            pc['program'] = int(program)
                        if channel:
                            pc['channel'] = int(channel)
                            
                        self.modified = True
                        print(f"Updated program change: {pc['program']} on channel {pc['channel']}")
                    else:
                        print("Invalid index")
                except ValueError:
                    print("Please enter valid numbers")
                    
            elif choice == '3' and preset.program_changes:
                try:
                    idx = int(input(f"Enter index to delete (1-{len(preset.program_changes)}): ")) - 1
                    if 0 <= idx < len(preset.program_changes):
                        del preset.program_changes[idx]
                        self.modified = True
                        print("Program change deleted")
                    else:
                        print("Invalid index")
                except ValueError:
                    print("Please enter a valid number")
                    
            elif choice == '4':
                break
                
    def _edit_control_changes(self, preset):
        """
        Edit control changes in a preset.
        
        Args:
            preset (Preset): The preset to edit
        """
        while True:
            print("\nControl Changes")
            print("--------------")
            if not preset.control_changes:
                print("No control changes defined")
            else:
                for i, cc in enumerate(preset.control_changes):
                    print(f"{i+1}. Controller: {cc['controller']}, Value: {cc['value']}, Channel: {cc['channel']}")
            
            print("\n1. Add control change")
            if preset.control_changes:
                print("2. Edit control change")
                print("3. Delete control change")
            print("4. Back to preset menu")
            
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                try:
                    controller = int(input("Enter controller number (0-127): "))
                    value = int(input("Enter value (0-127): "))
                    channel = int(input("Enter channel (0-15) [0]: ") or "0")
                    
                    if (0 <= controller <= 127 and 0 <= value <= 127 and 0 <= channel <= 15):
                        preset.add_control_change(controller, value, channel)
                        self.modified = True
                        print(f"Added control change: {controller}={value} on channel {channel}")
                    else:
                        print("Invalid values. Controller and value must be 0-127, channel 0-15.")
                except ValueError:
                    print("Please enter valid numbers")
                    
            elif choice == '2' and preset.control_changes:
                try:
                    idx = int(input(f"Enter index to edit (1-{len(preset.control_changes)}): ")) - 1
                    if 0 <= idx < len(preset.control_changes):
                        cc = preset.control_changes[idx]
                        controller = input(f"Enter controller number (0-127) [{cc['controller']}]: ")
                        value = input(f"Enter value (0-127) [{cc['value']}]: ")
                        channel = input(f"Enter channel (0-15) [{cc['channel']}]: ")
                        
                        if controller:
                            cc['controller'] = int(controller)
                        if value:
                            cc['value'] = int(value)
                        if channel:
                            cc['channel'] = int(channel)
                            
                        self.modified = True
                        print(f"Updated control change: {cc['controller']}={cc['value']} on channel {cc['channel']}")
                    else:
                        print("Invalid index")
                except ValueError:
                    print("Please enter valid numbers")
                    
            elif choice == '3' and preset.control_changes:
                try:
                    idx = int(input(f"Enter index to delete (1-{len(preset.control_changes)}): ")) - 1
                    if 0 <= idx < len(preset.control_changes):
                        del preset.control_changes[idx]
                        self.modified = True
                        print("Control change deleted")
                    else:
                        print("Invalid index")
                except ValueError:
                    print("Please enter a valid number")
                    
            elif choice == '4':
                break
    
    def browse_presets(self):
        """Browse and edit presets"""
        while True:
            print("\nFCB1010 Presets")
            print("--------------")
            
            if not self.presets:
                print("No presets loaded")
            else:
                # Show a paginated list of presets
                page_size = 10
                total_pages = (len(self.presets) + page_size - 1) // page_size
                
                page = 0
                while True:
                    start_idx = page * page_size
                    end_idx = min(start_idx + page_size, len(self.presets))
                    
                    print(f"\nShowing presets {start_idx+1}-{end_idx} of {len(self.presets)}")
                    print(f"Page {page+1} of {total_pages}")
                    print("-----------------")
                    
                    for i in range(start_idx, end_idx):
                        p = self.presets[i]
                        print(f"{i+1}. #{p.preset_number}: {p.name}")
                    
                    if total_pages > 1:
                        print("\nn: Next page, p: Previous page, s: Select preset, q: Back to main menu")
                    else:
                        print("\ns: Select preset, q: Back to main menu")
                    
                    choice = input("\nEnter choice: ")
                    
                    if choice.lower() == 'n' and page < total_pages - 1:
                        page += 1
                    elif choice.lower() == 'p' and page > 0:
                        page -= 1
                    elif choice.lower() == 's':
                        try:
                            idx = int(input(f"Enter preset number (1-{len(self.presets)}): ")) - 1
                            if 0 <= idx < len(self.presets):
                                self.edit_preset(self.presets[idx])
                            else:
                                print("Invalid preset number")
                        except ValueError:
                            print("Please enter a valid number")
                    elif choice.lower() == 'q':
                        break
                
            print("\n1. Create new preset")
            print("2. Back to main menu")
            
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                new_preset = self.create_new_preset()
                if new_preset:
                    self.edit_preset(new_preset)
            elif choice == '2':
                break
    
    def connect_to_fcb1010(self):
        """Connect to FCB1010 hardware"""
        try:
            self.fcb = FCB1010()
            print("Connected to FCB1010")
            return True
        except Exception as e:
            logger.error(f"Error connecting to FCB1010: {e}")
            print(f"Error connecting to FCB1010: {e}")
            return False
            
    def send_preset_to_fcb1010(self):
        """Send a preset to the FCB1010"""
        if not self.fcb:
            print("Not connected to FCB1010")
            return
            
        if not self.presets:
            print("No presets loaded")
            return
            
        try:
            # List presets
            print("\nSelect preset to send:")
            for i, p in enumerate(self.presets):
                print(f"{i+1}. #{p.preset_number}: {p.name}")
                
            idx = int(input(f"Enter preset number (1-{len(self.presets)}): ")) - 1
            if 0 <= idx < len(self.presets):
                preset = self.presets[idx]
                print(f"Sending preset {preset.preset_number}: {preset.name}")
                
                # Send program changes
                for pc in preset.program_changes:
                    self.fcb.send_program_change(pc['program'], pc['channel'])
                    
                # Send control changes
                for cc in preset.control_changes:
                    self.fcb.send_control_change(cc['controller'], cc['value'], cc['channel'])
                    
                print("Preset sent successfully")
            else:
                print("Invalid preset number")
        except ValueError:
            print("Please enter a valid number")
        except Exception as e:
            logger.error(f"Error sending preset: {e}")
            print(f"Error sending preset: {e}")

    def run(self):
        """Run the editor interface"""
        connected = False
        
        while True:
            print("\nFCB1010 Editor")
            print("=============")
            
            print(f"Current file: {self.current_file or 'None'}")
            print(f"Presets: {len(self.presets)}")
            print(f"Modified: {'Yes' if self.modified else 'No'}")
            print(f"Connected to FCB1010: {'Yes' if self.fcb else 'No'}")
            
            print("\n1. Load presets from file")
            print("2. Save presets")
            print("3. Save presets as...")
            print("4. Browse/edit presets")
            
            if self.fcb:
                print("5. Send preset to FCB1010")
                print("6. Disconnect from FCB1010")
            else:
                print("5. Connect to FCB1010")
                
            print("7. Quit")
            
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                filename = input("Enter filename to load: ")
                if filename:
                    if self.modified:
                        save = input("Current presets have been modified. Save first? (y/n): ")
                        if save.lower() == 'y':
                            self.save_presets()
                    self.load_presets(filename)
                    
            elif choice == '2':
                self.save_presets()
                
            elif choice == '3':
                filename = input("Enter filename to save as: ")
                if filename:
                    self.save_presets(filename)
                    
            elif choice == '4':
                self.browse_presets()
                
            elif choice == '5':
                if self.fcb:
                    self.send_preset_to_fcb1010()
                else:
                    if self.connect_to_fcb1010():
                        connected = True
                    
            elif choice == '6' and self.fcb:
                self.fcb.close()
                self.fcb = None
                print("Disconnected from FCB1010")
                
            elif choice == '7':
                if self.modified:
                    save = input("Presets have been modified. Save before quitting? (y/n): ")
                    if save.lower() == 'y':
                        self.save_presets()
                
                if self.fcb:
                    self.fcb.close()
                    
                print("Goodbye!")
                break

def main():
    """Main function"""
    editor = PresetEditor()
    
    # If a filename is provided as a command-line argument, try to load it
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if os.path.exists(filename):
            editor.load_presets(filename)
        else:
            print(f"File not found: {filename}")
    
    editor.run()

if __name__ == "__main__":
    main()
