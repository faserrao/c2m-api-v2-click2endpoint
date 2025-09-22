#!/usr/bin/env python3
"""Test the simple EBNF parser"""

from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent))

from simple_ebnf_parser import SimpleEBNFParser

def main():
    ebnf_path = Path(__file__).parent.parent.parent / "c2mapiv2-dd-with-questions.ebnf"
    
    print(f"Testing Simple EBNF Parser with: {ebnf_path}")
    
    parser = SimpleEBNFParser(str(ebnf_path))
    parser.parse()
    
    print(f"\nFound {len(parser.use_cases)} use cases:")
    for name, info in parser.use_cases.items():
        print(f"  {name}: {info['endpoint']}")
    
    print(f"\nFound {len(parser.productions)} productions")
    
    # Test with submitSingleDocWithTemplateParams
    test_case = "submitSingleDocWithTemplateParams"
    print(f"\n\nTesting parameter extraction for: {test_case}")
    
    params = parser.get_use_case_parameters(test_case)
    print(f"\nExtracted {len(params)} parameters:")
    for param in params:
        print(f"  {param['name']}: {param['question']} (type: {param['type']})")
    
    # Generate flow
    print(f"\n\nGenerating parameter flow:")
    flow = parser.generate_parameter_flow(test_case)
    print(json.dumps(flow, indent=2))

if __name__ == "__main__":
    main()