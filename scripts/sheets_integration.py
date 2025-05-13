#!/usr/bin/env python3
"""
FCB1010 Editor - Google Sheets Integration

This script allows you to export and import FCB1010 presets to/from Google Sheets,
making it easier to edit and manage your presets in a spreadsheet.
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Add the parent directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fcb1010 import FCB1010, Preset

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Scope for Google Sheets API
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

class SheetsInterface:
    """Interface for working with Google Sheets"""
    
    def __init__(self, credentials_file='credentials.json'):
        """
        Initialize the Google Sheets interface.
        
        Args:
            credentials_file (str): Path to the Google API credentials file
        """
        self.credentials_file = credentials_file
        self.client = None
        
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, SCOPES)
            self.client = gspread.authorize(credentials)
            logger.info("Successfully authenticated with Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
            
    def open_sheet(self, spreadsheet_name, worksheet_name='Presets'):
        """
        Open a Google Sheet.
        
        Args:
            spreadsheet_name (str): Name of the spreadsheet
            worksheet_name (str): Name of the worksheet
            
        Returns:
            Worksheet or None if opening failed
        """
        try:
            spreadsheet = self.client.open(spreadsheet_name)
            worksheet = spreadsheet.worksheet(worksheet_name)
            logger.info(f"Opened worksheet: {worksheet_name}")
            return worksheet
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet '{spreadsheet_name}' not found")
            return None
        except Exception as e:
            logger.error(f"Error opening sheet: {e}")
            return None
            
    def create_presets_sheet(self, spreadsheet_name):
        """
        Create a new spreadsheet for FCB1010 presets.
        
        Args:
            spreadsheet_name (str): Name of the new spreadsheet
            
        Returns:
            Worksheet or None if creation failed
        """
        try:
            spreadsheet = self.client.create(spreadsheet_name)
            worksheet = spreadsheet.sheet1
            worksheet.update_title('Presets')
            
            # Set up the header row
            headers = [
                'Preset Number', 'Name', 
                'PC1 Program', 'PC1 Channel',
                'PC2 Program', 'PC2 Channel',
                'CC1 Controller', 'CC1 Value', 'CC1 Channel',
                'CC2 Controller', 'CC2 Value', 'CC2 Channel',
                'Notes'
            ]
            worksheet.append_row(headers)
            
            # Format the header row
            worksheet.format('A1:M1', {
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                'textFormat': {'bold': True}
            })
            
            logger.info(f"Created new spreadsheet: {spreadsheet_name}")
            return worksheet
        except Exception as e:
            logger.error(f"Error creating sheet: {e}")
            return None
    
    def export_presets_to_sheet(self, presets, worksheet):
        """
        Export presets to a Google Sheet.
        
        Args:
            presets (list): List of Preset objects or dictionaries
            worksheet: Google Sheets worksheet
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clear existing data (except header)
            if worksheet.row_count > 1:
                worksheet.delete_rows(2, worksheet.row_count - 1)
            
            # Prepare data rows
            rows = []
            for p in presets:
                preset = p if isinstance(p, dict) else p.to_dict()
                
                # Basic preset info
                row = [preset['preset_number'], preset['name']]
                
                # Program changes (up to 2)
                pcs = preset.get('program_changes', [])
                for i in range(2):
                    if i < len(pcs):
                        row.append(pcs[i].get('program', ''))
                        row.append(pcs[i].get('channel', 0))
                    else:
                        row.append('')
                        row.append('')
                
                # Control changes (up to 2)
                ccs = preset.get('control_changes', [])
                for i in range(2):
                    if i < len(ccs):
                        row.append(ccs[i].get('controller', ''))
                        row.append(ccs[i].get('value', ''))
                        row.append(ccs[i].get('channel', 0))
                    else:
                        row.append('')
                        row.append('')
                        row.append('')
                
                # Notes
                row.append('')
                
                rows.append(row)
            
            # Add all rows at once (more efficient)
            if rows:
                worksheet.append_rows(rows)
            
            logger.info(f"Exported {len(rows)} presets to Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Error exporting presets: {e}")
            return False
    
    def import_presets_from_sheet(self, worksheet):
        """
        Import presets from a Google Sheet.
        
        Args:
            worksheet: Google Sheets worksheet
            
        Returns:
            list: List of Preset objects or None if import failed
        """
        try:
            # Get all data
            data = worksheet.get_all_values()
            
            # Skip header row
            data = data[1:]
            
            presets = []
            for row in data:
                if not row[0] or not row[0].isdigit():
                    continue  # Skip invalid rows
                
                preset_number = int(row[0])
                name = row[1]
                
                preset = Preset(preset_number, name)
                
                # Import program changes
                if row[2]:  # PC1 Program
                    try:
                        program = int(row[2])
                        channel = int(row[3]) if row[3] else 0
                        preset.add_program_change(program, channel)
                    except ValueError:
                        pass
                
                if row[4]:  # PC2 Program
                    try:
                        program = int(row[4])
                        channel = int(row[5]) if row[5] else 0
                        preset.add_program_change(program, channel)
                    except ValueError:
                        pass
                
                # Import control changes
                if row[6]:  # CC1 Controller
                    try:
                        controller = int(row[6])
                        value = int(row[7]) if row[7] else 0
                        channel = int(row[8]) if row[8] else 0
                        preset.add_control_change(controller, value, channel)
                    except ValueError:
                        pass
                
                if row[9]:  # CC2 Controller
                    try:
                        controller = int(row[9])
                        value = int(row[10]) if row[10] else 0
                        channel = int(row[11]) if row[11] else 0
                        preset.add_control_change(controller, value, channel)
                    except ValueError:
                        pass
                
                presets.append(preset)
            
            logger.info(f"Imported {len(presets)} presets from Google Sheets")
            return presets
        except Exception as e:
            logger.error(f"Error importing presets: {e}")
            return None

def main():
    """Main function for the Google Sheets integration tool"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python sheets_integration.py export <json_file> <spreadsheet_name>")
        print("  python sheets_integration.py import <spreadsheet_name> <json_file>")
        print("  python sheets_integration.py create <spreadsheet_name>")
        return
    
    command = sys.argv[1]
    
    if not os.path.exists('credentials.json'):
        print("Error: Google API credentials file 'credentials.json' not found.")
        print("Please download it from the Google API Console and place it in the current directory.")
        return
    
    sheets = SheetsInterface()
    if not sheets.authenticate():
        print("Authentication failed. Please check your credentials file.")
        return
    
    if command == 'export':
        if len(sys.argv) < 4:
            print("Usage: python sheets_integration.py export <json_file> <spreadsheet_name>")
            return
        
        json_file = sys.argv[2]
        spreadsheet_name = sys.argv[3]
        
        try:
            with open(json_file, 'r') as f:
                presets_data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return
        
        # Open existing sheet or create new one
        worksheet = sheets.open_sheet(spreadsheet_name)
        if not worksheet:
            print(f"Creating new spreadsheet '{spreadsheet_name}'...")
            worksheet = sheets.create_presets_sheet(spreadsheet_name)
            if not worksheet:
                print("Failed to create spreadsheet")
                return
        
        # Export presets
        if sheets.export_presets_to_sheet(presets_data, worksheet):
            print(f"Successfully exported {len(presets_data)} presets to '{spreadsheet_name}'")
    
    elif command == 'import':
        if len(sys.argv) < 4:
            print("Usage: python sheets_integration.py import <spreadsheet_name> <json_file>")
            return
        
        spreadsheet_name = sys.argv[2]
        json_file = sys.argv[3]
        
        # Open the sheet
        worksheet = sheets.open_sheet(spreadsheet_name)
        if not worksheet:
            print(f"Spreadsheet '{spreadsheet_name}' not found or couldn't be opened")
            return
        
        # Import presets
        presets = sheets.import_presets_from_sheet(worksheet)
        if presets:
            # Convert to dict for JSON serialization
            presets_data = [p.to_dict() for p in presets]
            
            try:
                with open(json_file, 'w') as f:
                    json.dump(presets_data, f, indent=2)
                print(f"Successfully imported {len(presets)} presets to '{json_file}'")
            except Exception as e:
                print(f"Error writing to JSON file: {e}")
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("Usage: python sheets_integration.py create <spreadsheet_name>")
            return
        
        spreadsheet_name = sys.argv[2]
        worksheet = sheets.create_presets_sheet(spreadsheet_name)
        if worksheet:
            print(f"Successfully created spreadsheet '{spreadsheet_name}'")
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: export, import, create")

if __name__ == "__main__":
    main()
