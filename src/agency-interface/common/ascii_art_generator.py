#!/usr/bin/env python3
"""
ASCII Art Generator for Agency Interface

This module generates ASCII art for agency banners based on templates or dynamic generation.
It supports both template-based rendering and on-the-fly generation when templates aren't available.
"""

import os
import json
import re
from typing import Dict, Optional, List, Tuple

class ASCIIArtGenerator:
    """
    Generator for agency ASCII art banners.
    """
    
    def __init__(self, template_dir: str, config_file: Optional[str] = None) -> None:
        """
        Initialize the ASCII art generator.
        
        Args:
            template_dir: Directory containing ASCII art templates
            config_file: Optional path to configuration file
        """
        self.template_dir = template_dir
        self.config_file = config_file
        self.templates = {}
        self.config = self._load_config()
        self._load_templates()
    
    def _load_config(self) -> dict:
        """Load configuration file if provided."""
        if not self.config_file or not os.path.exists(self.config_file):
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in config file: {self.config_file}")
            return {}
    
    def _load_templates(self) -> None:
        """Load ASCII art templates from the template directory."""
        if not os.path.exists(self.template_dir):
            print(f"Warning: Template directory does not exist: {self.template_dir}")
            return
        
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.txt'):
                agency_id = filename.replace('_ascii.txt', '')
                template_path = os.path.join(self.template_dir, filename)
                
                try:
                    with open(template_path, 'r') as f:
                        self.templates[agency_id] = f.read()
                except IOError:
                    print(f"Warning: Failed to load template: {template_path}")
    
    def generate_art(self, agency: str, agency_name: Optional[str] = None) -> str:
        """
        Generate ASCII art for the specified agency.
        
        Args:
            agency: Agency identifier (e.g., HHS, DOD)
            agency_name: Optional full name of the agency
            
        Returns:
            ASCII art for the agency
        """
        # Try to get from templates first
        agency_id = agency.lower()
        if agency_id in self.templates:
            return self.templates[agency_id]
        
        # If no template exists, generate dynamically
        return self._generate_dynamic_art(agency, agency_name)
    
    def _generate_dynamic_art(self, agency: str, agency_name: Optional[str] = None) -> str:
        """
        Dynamically generate ASCII art for an agency.
        
        Args:
            agency: Agency identifier (e.g., HHS, DOD)
            agency_name: Optional full name of the agency
            
        Returns:
            Dynamically generated ASCII art
        """
        if not agency_name:
            # Try to look up the agency name in the config
            if 'agencies' in self.config:
                for agency_info in self.config['agencies']:
                    if agency_info.get('acronym', '').lower() == agency.lower():
                        agency_name = agency_info.get('name', '')
                        break
            
            # If still no name, use the agency ID
            if not agency_name:
                agency_name = agency.upper()
        
        # Create agency acronym in large text
        agency_large = self._create_large_text(agency.upper())
        
        # Determine box width based on text length
        name_length = len(agency_name) + 16  # Add padding
        box_width = max(name_length, len(agency_large[0]) + 8)
        
        # Create the ASCII art
        art = []
        art.append(' ' + '█' * box_width + ' ')
        art.append(' █' + ' ' * (box_width - 2) + '█ ')
        
        # Add agency large text, centered
        for line in agency_large:
            padding = (box_width - 2 - len(line)) // 2
            art.append(' █' + ' ' * padding + line + ' ' * (box_width - 2 - padding - len(line)) + '█ ')
        
        # Add empty line
        art.append(' █' + ' ' * (box_width - 2) + '█ ')
        
        # Add agency name line, centered
        name_text = f"       {agency_name}      "
        name_padding = (box_width - 2 - len(name_text)) // 2
        art.append(' █' + ' ' * name_padding + name_text + ' ' * (box_width - 2 - name_padding - len(name_text)) + '█ ')
        
        # Add closing line
        art.append(' █' + ' ' * (box_width - 2) + '█ ')
        art.append(' ' + '█' * box_width + ' ')
        
        return '\n'.join(art)
    
    def _create_large_text(self, text: str) -> List[str]:
        """
        Create large ASCII text for the agency acronym.
        
        Args:
            text: Text to render in large ASCII
            
        Returns:
            List of strings representing the large ASCII text
        """
        # Define simple ASCII art for each letter (3x5 grid)
        letter_art = {
            'A': [
                '   █████   ',
                '  ██   ██  ',
                ' ███████  ',
                ' ██   ██  ',
                '██    ██ '
            ],
            'B': [
                ' ██████   ',
                ' ██   ██  ',
                ' ██████   ',
                ' ██   ██  ',
                ' ██████   '
            ],
            'C': [
                '  █████   ',
                ' ██   ██  ',
                ' ██       ',
                ' ██   ██  ',
                '  █████   '
            ],
            'D': [
                ' ██████   ',
                ' ██   ██  ',
                ' ██   ██  ',
                ' ██   ██  ',
                ' ██████   '
            ],
            'E': [
                ' ███████  ',
                ' ██       ',
                ' █████    ',
                ' ██       ',
                ' ███████  '
            ],
            'F': [
                ' ███████  ',
                ' ██       ',
                ' █████    ',
                ' ██       ',
                ' ██       '
            ],
            'G': [
                '  █████   ',
                ' ██       ',
                ' ██  ███  ',
                ' ██   ██  ',
                '  █████   '
            ],
            'H': [
                ' ██   ██  ',
                ' ██   ██  ',
                ' ███████  ',
                ' ██   ██  ',
                ' ██   ██  '
            ],
            'I': [
                ' ███████  ',
                '    ██    ',
                '    ██    ',
                '    ██    ',
                ' ███████  '
            ],
            'J': [
                '      ██  ',
                '      ██  ',
                '      ██  ',
                ' ██   ██  ',
                '  █████   '
            ],
            'K': [
                ' ██   ██  ',
                ' ██  ██   ',
                ' █████    ',
                ' ██  ██   ',
                ' ██   ██  '
            ],
            'L': [
                ' ██       ',
                ' ██       ',
                ' ██       ',
                ' ██       ',
                ' ███████  '
            ],
            'M': [
                ' ██    ██ ',
                ' ███  ███ ',
                ' ██ ██ ██ ',
                ' ██    ██ ',
                ' ██    ██ '
            ],
            'N': [
                ' ██   ██  ',
                ' ███  ██  ',
                ' ██ █ ██  ',
                ' ██  ███  ',
                ' ██   ██  '
            ],
            'O': [
                '  █████   ',
                ' ██   ██  ',
                ' ██   ██  ',
                ' ██   ██  ',
                '  █████   '
            ],
            'P': [
                ' ██████   ',
                ' ██   ██  ',
                ' ██████   ',
                ' ██       ',
                ' ██       '
            ],
            'Q': [
                '  █████   ',
                ' ██   ██  ',
                ' ██   ██  ',
                ' ██  ███  ',
                '  ████ ██ '
            ],
            'R': [
                ' ██████   ',
                ' ██   ██  ',
                ' ██████   ',
                ' ██  ██   ',
                ' ██   ██  '
            ],
            'S': [
                '  █████   ',
                ' ██       ',
                '  █████   ',
                '      ██  ',
                '  █████   '
            ],
            'T': [
                ' ███████  ',
                '    ██    ',
                '    ██    ',
                '    ██    ',
                '    ██    '
            ],
            'U': [
                ' ██   ██  ',
                ' ██   ██  ',
                ' ██   ██  ',
                ' ██   ██  ',
                '  █████   '
            ],
            'V': [
                ' ██   ██  ',
                ' ██   ██  ',
                ' ██   ██  ',
                '  ██ ██   ',
                '   ███    '
            ],
            'W': [
                ' ██    ██ ',
                ' ██    ██ ',
                ' ██ ██ ██ ',
                ' ███  ███ ',
                ' ██    ██ '
            ],
            'X': [
                ' ██   ██  ',
                '  ██ ██   ',
                '   ███    ',
                '  ██ ██   ',
                ' ██   ██  '
            ],
            'Y': [
                ' ██   ██  ',
                '  ██ ██   ',
                '   ███    ',
                '    ██    ',
                '    ██    '
            ],
            'Z': [
                ' ███████  ',
                '     ██   ',
                '   ██     ',
                ' ██       ',
                ' ███████  '
            ],
            '-': [
                '          ',
                '          ',
                ' ███████  ',
                '          ',
                '          '
            ],
            '_': [
                '          ',
                '          ',
                '          ',
                '          ',
                ' ███████  '
            ],
            '.': [
                '          ',
                '          ',
                '          ',
                '          ',
                '   ██     '
            ],
            ' ': [
                '          ',
                '          ',
                '          ',
                '          ',
                '          '
            ]
        }
        
        # Initialize result with empty lines
        result = [''] * 5
        
        # Add each letter's art
        for char in text:
            if char in letter_art:
                for i in range(5):
                    result[i] += letter_art[char][i]
            else:
                # Use space for unknown characters
                for i in range(5):
                    result[i] += letter_art[' '][i]
        
        return result
    
    def save_template(self, agency: str, art: str) -> bool:
        """
        Save a generated ASCII art as a template.
        
        Args:
            agency: Agency identifier (e.g., HHS, DOD)
            art: ASCII art to save
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.template_dir):
            try:
                os.makedirs(self.template_dir)
            except OSError:
                print(f"Error: Failed to create template directory: {self.template_dir}")
                return False
        
        template_path = os.path.join(self.template_dir, f"{agency.lower()}_ascii.txt")
        
        try:
            with open(template_path, 'w') as f:
                f.write(art)
            
            # Add to loaded templates
            self.templates[agency.lower()] = art
            
            return True
        except IOError:
            print(f"Error: Failed to save template: {template_path}")
            return False
    
    def generate_all_agencies(self, agencies: List[Dict]) -> Dict[str, str]:
        """
        Generate ASCII art for all provided agencies.
        
        Args:
            agencies: List of agency dictionaries with acronym and name
            
        Returns:
            Dictionary mapping agency IDs to ASCII art
        """
        result = {}
        
        for agency in agencies:
            acronym = agency.get('acronym', '')
            name = agency.get('name', '')
            
            if acronym:
                art = self.generate_art(acronym, name)
                result[acronym.lower()] = art
                
                # Save as template for future use
                self.save_template(acronym, art)
        
        return result

def main():
    """Main function for running as a script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ASCII art for agencies")
    parser.add_argument("--agency", help="Agency acronym to generate art for")
    parser.add_argument("--agency-name", help="Full agency name")
    parser.add_argument("--template-dir", default="templates", help="Directory for ASCII art templates")
    parser.add_argument("--config-file", help="Path to configuration file")
    parser.add_argument("--save", action="store_true", help="Save generated art as a template")
    parser.add_argument("--generate-all", action="store_true", help="Generate art for all agencies in the config")
    
    args = parser.parse_args()
    
    generator = ASCIIArtGenerator(args.template_dir, args.config_file)
    
    if args.generate_all and args.config_file:
        try:
            with open(args.config_file, 'r') as f:
                config = json.load(f)
                if 'agencies' in config:
                    arts = generator.generate_all_agencies(config['agencies'])
                    print(f"Generated ASCII art for {len(arts)} agencies")
                else:
                    print("Error: No agencies found in config file")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}")
    elif args.agency:
        art = generator.generate_art(args.agency, args.agency_name)
        print(art)
        
        if args.save:
            if generator.save_template(args.agency, art):
                print(f"Saved template for {args.agency}")
            else:
                print(f"Failed to save template for {args.agency}")
    else:
        print("Error: Either --agency or --generate-all must be specified")

if __name__ == "__main__":
    main()