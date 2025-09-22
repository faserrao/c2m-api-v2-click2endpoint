#!/usr/bin/env python3
"""Test the document choice requirement for Use Case 1 option 3"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from scripts.ebnf_template_parser import EBNFTemplateParser

def test_document_choice():
    """Test that option 3 requires document choice"""
    
    ebnf_path = Path(__file__).parent.parent / "c2mapiv2-dd.ebnf"
    parser = EBNFTemplateParser(str(ebnf_path))
    parser.parse()
    
    # Get Use Case 1
    logic = parser.template_logic.get('submitSingleDocWithTemplateParams')
    
    if not logic:
        print("ERROR: Could not find submitSingleDocWithTemplateParams")
        return
    
    print("Use Case 1: submitSingleDocWithTemplateParams")
    print(f"Number of options: {len(logic.options)}")
    print()
    
    for i, option in enumerate(logic.options):
        print(f"Option {i+1}:")
        print(f"  From template: {option.from_template}")
        print(f"  From API: {option.from_api}")
        print(f"  Requires document choice: {option.requires_document_choice}")
        print()
    
    # Generate full UI flow
    ui_flow = parser.generate_ui_flow('submitSingleDocWithTemplateParams')
    
    print("UI Flow Template Options:")
    for opt in ui_flow['questions'][0]['options']:
        print(f"\n{opt['label']}:")
        print(f"  Value: {opt['value']}")
        print(f"  Requires document choice: {opt.get('requires_document_choice', False)}")

if __name__ == "__main__":
    test_document_choice()