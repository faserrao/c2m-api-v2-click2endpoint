#!/usr/bin/env python3
"""
Demo script to show the document choice flow for Use Case 1
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ebnf_template_parser import EBNFTemplateParser

def demo():
    ebnf_path = Path(__file__).parent.parent / "c2mapiv2-dd.ebnf"
    parser = EBNFTemplateParser(str(ebnf_path))
    parser.parse()
    
    print("=" * 60)
    print("C2M API - Use Case 1: Single Document with Job Template")
    print("=" * 60)
    print("\nQuestion 1: What information will come from the template?")
    print("\n1. Template provides: document (you provide: recipients)")
    print("2. Template provides: recipients (you provide: document)")
    print("3. Template provides: job options only (you provide: document & recipients)")
    
    print("\n[User selects option 3]")
    print("\n" + "-" * 40)
    print("Since you're providing your own addresses...")
    print("\nQuestion 2: How will the document be provided?")
    print("\n1. Document comes from the job template")
    print("2. Document provided in API call")
    
    print("\n[If user selects 1 - Document from template]:")
    print("  → You need to provide: Recipients only")
    print("\n[If user selects 2 - Document from API]:")
    print("  → You need to provide: Document AND Recipients")
    
    print("\n" + "-" * 40)
    print("\nThis additional question ensures flexibility:")
    print("- Job templates can contain documents")
    print("- Even when not using template addresses")
    print("- Users can choose document source separately")

if __name__ == "__main__":
    demo()