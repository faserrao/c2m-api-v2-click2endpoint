#!/usr/bin/env python3
"""Test the EBNF template parser"""

from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent))

from ebnf_template_parser import EBNFTemplateParser
import re

def main():
    ebnf_path = Path(__file__).parent.parent.parent / "c2mapiv2-dd.ebnf"
    
    print(f"Testing EBNF Template Parser with: {ebnf_path}")
    
    parser = EBNFTemplateParser(str(ebnf_path))
    
    # Debug: Read file content
    with open(ebnf_path, 'r') as f:
        content = f.read()
    
    # Look for TEMPLATE in comments - EBNF uses (* *) not /* */
    template_blocks = re.findall(r'\(\*.*?TEMPLATE.*?\*\)', content, re.DOTALL)
    print(f"\nFound {len(template_blocks)} comment blocks containing TEMPLATE")
    
    # Also try a simpler search
    if '"TEMPLATE"' in content:
        print("Found quoted TEMPLATE in file")
        # Count occurrences
        count = content.count('"TEMPLATE"')
        print(f"Number of occurrences: {count}")
    
    parser.parse()
    
    print(f"\nFound {len(parser.template_logic)} endpoints with template logic:")
    for name, logic in parser.template_logic.items():
        print(f"\n{name}:")
        print(f"  Endpoint: {logic.endpoint_path}")
        print(f"  Options:")
        for i, opt in enumerate(logic.options):
            print(f"    Option {i+1}:")
            print(f"      From template: {opt.from_template}")
            print(f"      From API: {opt.from_api}")
        print(f"  Always required: {logic.always_required}")
    
    # Test UI flow generation
    print("\n\nGenerating UI flow for submitSingleDocWithTemplateParams:")
    flow = parser.generate_ui_flow("submitSingleDocWithTemplateParams")
    print(json.dumps(flow, indent=2))
    
    print("\n\nGenerating UI flow for mergeMultiDocWithTemplateParams:")
    flow = parser.generate_ui_flow("mergeMultiDocWithTemplateParams")
    print(json.dumps(flow, indent=2))

if __name__ == "__main__":
    main()