#!/usr/bin/env python3
"""
Test script for EBNF parser
"""

from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ebnf_parser import EBNFParser
import json

def main():
    # Path to EBNF file
    ebnf_path = Path(__file__).parent.parent.parent / "c2mapiv2-dd-with-questions.ebnf"
    
    print(f"Loading EBNF from: {ebnf_path}")
    
    if not ebnf_path.exists():
        print(f"ERROR: EBNF file not found at {ebnf_path}")
        return
    
    # Create parser and parse
    parser = EBNFParser(str(ebnf_path))
    parser.parse()
    
    # Display results
    print(f"\nFound {len(parser.use_cases)} use cases:")
    for name, use_case in parser.use_cases.items():
        print(f"\n{name}:")
        print(f"  Endpoint: {use_case.endpoint}")
        print(f"  Question: {use_case.question}")
        print(f"  Parameters: {', '.join(use_case.parameters)}")
    
    # Test generating Q&A tree for a specific use case
    test_case = "submitSingleDocWithTemplateParams"
    print(f"\n\nGenerating Q&A tree for: {test_case}")
    qa_tree = parser.generate_qa_tree(test_case)
    
    if qa_tree:
        print(json.dumps(qa_tree, indent=2))
    else:
        print("Failed to generate Q&A tree")
    
    # Show all extracted questions
    print(f"\n\nAll extracted parameter questions ({len(parser.questions)}):")
    for param, question in parser.questions.items():
        print(f"  {param}: {question}")

if __name__ == "__main__":
    main()