#!/usr/bin/env python3
"""Test the EBNF QA parser"""

from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent))

from ebnf_qa_parser import generate_qa_tree_for_endpoint, extract_questions

def main():
    ebnf_path = Path(__file__).parent.parent.parent / "c2mapiv2-dd-with-questions.ebnf"
    
    print(f"Testing EBNF QA Parser with: {ebnf_path}")
    
    # Test extracting questions
    with open(ebnf_path, 'r') as f:
        text = f.read()
    
    questions = extract_questions(text)
    print(f"\nExtracted {len(questions)} questions:")
    for param, question in list(questions.items())[:10]:
        print(f"  {param}: {question}")
    
    # Test generating QA tree for submitSingleDocWithTemplateParams
    endpoint = "submitSingleDocWithTemplateParams"
    print(f"\n\nGenerating QA tree for: {endpoint}")
    
    tree_data = generate_qa_tree_for_endpoint(str(ebnf_path), endpoint)
    
    if tree_data:
        print(f"Endpoint: {tree_data['endpoint']}")
        print(f"Use case: {tree_data['use_case']}")
        print("\nQA Tree:")
        print(json.dumps(tree_data['qa_tree'], indent=2))
    else:
        print("Failed to generate QA tree")

if __name__ == "__main__":
    main()