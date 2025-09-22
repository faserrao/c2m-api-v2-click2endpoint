#!/usr/bin/env python3
"""Test the integrated solution with template parser"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scripts.endpoint_mapper import EndpointMapper
from scripts.ebnf_template_parser import EBNFTemplateParser

def test_integration():
    """Test that integration works properly"""
    
    # Test mapper
    mapper = EndpointMapper()
    print("Testing Endpoint Mapper:")
    print(f"  /jobs/single-doc-job-template -> {mapper.endpoint_to_usecase('/jobs/single-doc-job-template')}")
    print(f"  /jobs/multi-doc-merge-job-template -> {mapper.endpoint_to_usecase('/jobs/multi-doc-merge-job-template')}")
    
    # Test parser
    ebnf_path = Path(__file__).parent.parent / "c2mapiv2-dd.ebnf"
    parser = EBNFTemplateParser(str(ebnf_path))
    parser.parse()
    
    print("\nTesting EBNF Template Parser:")
    print(f"  Found {len(parser.template_logic)} endpoints with template logic")
    print(f"  Found {len(parser.parameters)} parameter definitions")
    
    # Test UI flow generation for Use Case 1
    print("\nUI Flow for submitSingleDocWithTemplateParams:")
    flow = parser.generate_ui_flow("submitSingleDocWithTemplateParams")
    
    print(f"  Has template logic: {flow['has_template_logic']}")
    print(f"  Number of questions: {len(flow['questions'])}")
    print(f"  Template options:")
    
    for i, opt in enumerate(flow['questions'][0]['options']):
        print(f"    {i+1}. {opt['label']}")
    
    # Test Use Case 3
    print("\nUI Flow for mergeMultiDocWithTemplateParams:")
    flow3 = parser.generate_ui_flow("mergeMultiDocWithTemplateParams")
    
    print(f"  Has template logic: {flow3['has_template_logic']}")
    print(f"  Template options:")
    for i, opt in enumerate(flow3['questions'][0]['options']):
        print(f"    {i+1}. {opt['label']}")

if __name__ == "__main__":
    test_integration()