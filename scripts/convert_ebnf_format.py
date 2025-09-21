#!/usr/bin/env python3
"""
Convert EBNF from (* Question: ... *) format to (* Q name: ... *) format
This allows us to use the existing chat-ebnf-to-qa-generator parser
"""

import re
from pathlib import Path

def convert_ebnf_format(input_path: str, output_path: str):
    """Convert EBNF question format"""
    with open(input_path, 'r') as f:
        content = f.read()
    
    # Track all productions to add Q comments for them
    productions = {}
    
    # First pass: extract all production names and their questions
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Match production definition: name = ...
        prod_match = re.match(r'^(\w+)\s*=', line)
        if prod_match:
            prod_name = prod_match.group(1)
            
            # Look for inline question on the same or following lines
            question = None
            for j in range(i, min(i+5, len(lines))):
                q_match = re.search(r'\(\*\s*Question(?:\s*\(optional\))?\s*:\s*(.*?)\s*\*\)', lines[j])
                if q_match:
                    question = q_match.group(1).strip()
                    break
            
            productions[prod_name] = question
    
    # Convert inline questions to Q format
    converted_lines = []
    
    for line in lines:
        # Check if line has an inline Question comment
        if '(* Question' in line:
            # Extract the question
            q_match = re.search(r'\(\*\s*Question(?:\s*\(optional\))?\s*:\s*(.*?)\s*\*\)', line)
            if q_match:
                question_text = q_match.group(1).strip()
                is_optional = '(optional)' in line
                
                # Find the parameter name before the question
                before_comment = line.split('(*')[0].strip()
                param_name = None
                
                # Try different patterns to find parameter name
                patterns = [
                    r'\+\s*(\w+)\s*$',  # + paramName
                    r'\|\s*(\w+)\s*$',  # | paramName
                    r'^(\w+)\s*=',      # paramName = 
                    r'(\w+)\s*$'        # just paramName
                ]
                
                for pattern in patterns:
                    m = re.search(pattern, before_comment)
                    if m:
                        param_name = m.group(1)
                        break
                
                if param_name:
                    # Replace with Q format
                    new_comment = f"(* Q {param_name}: {question_text} *)"
                    line = line.replace(q_match.group(0), new_comment)
        
        converted_lines.append(line)
    
    # Join lines back
    converted = '\n'.join(converted_lines)
    
    # Add Q comments for productions that don't have them inline
    final_lines = []
    for line in converted.split('\n'):
        # Check if this is a production definition
        prod_match = re.match(r'^(\w+)\s*=', line)
        if prod_match:
            prod_name = prod_match.group(1)
            
            # Check if the production already has a Q comment above it
            prev_line_idx = len(final_lines) - 1
            has_q_comment = False
            if prev_line_idx >= 0:
                prev_line = final_lines[prev_line_idx]
                if f'(* Q {prod_name}:' in prev_line:
                    has_q_comment = True
            
            # Add Q comment if missing and we have a question for it
            if not has_q_comment and prod_name in productions and productions[prod_name]:
                final_lines.append(f"(* Q {prod_name}: {productions[prod_name]} *)")
        
        final_lines.append(line)
    
    # Write converted content
    with open(output_path, 'w') as f:
        f.write('\n'.join(final_lines))
    
    print(f"Converted {input_path} -> {output_path}")
    return output_path

def main():
    """Convert the EBNF file"""
    input_path = Path(__file__).parent.parent.parent / "c2mapiv2-dd-with-questions.ebnf"
    output_path = Path(__file__).parent.parent / "c2mapiv2-dd-converted.ebnf"
    
    convert_ebnf_format(str(input_path), str(output_path))
    
    print("\nTesting with chat-ebnf-to-qa-generator...")
    
    # Test with the original parser
    import subprocess
    import sys
    
    qa_gen_path = Path(__file__).parent.parent.parent / "chat-ebnf-to-qa-generator" / "chat-ebnf-to-qa-generator"
    
    result = subprocess.run([
        sys.executable,
        str(qa_gen_path / "ebnf_to_qa_tree.py"),
        "--input", str(output_path),
        "--endpoint", "submitSingleDocWithTemplateParams",
        "--out-json", "test_output.json",
        "--out-md", "test_output.md"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Success! Generated QA tree")
        # Read and display first part of output
        with open("test_output.json", 'r') as f:
            import json
            data = json.load(f)
            print("\nGenerated QA tree preview:")
            print(json.dumps(data, indent=2)[:500] + "...")
    else:
        print(f"Error: {result.stderr}")

if __name__ == "__main__":
    main()