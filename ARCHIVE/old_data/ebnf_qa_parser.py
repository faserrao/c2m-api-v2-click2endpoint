#!/usr/bin/env python3
"""
EBNF to QA Tree Parser - Adapted from chat-ebnf-to-qa-generator
This parser properly handles complex EBNF grammar with sequences, alternations, optionals, etc.
"""

import re
import json
from typing import Dict, Any, List, Optional

# Regex for Question comments: (* Question: ... *) or (* Question (optional): ... *)
Q_RE = re.compile(r'\(\*\s*Question(?:\s*\(optional\))?\s*:\s*(.*?)\s*\*\)')

def extract_questions(text):
    """Extract all Question comments from EBNF text"""
    questions = {}
    
    # Split into lines to associate questions with their parameters
    lines = text.split('\n')
    for i, line in enumerate(lines):
        match = Q_RE.search(line)
        if match:
            question_text = match.group(1).strip()
            
            # Look for the parameter name before the question on the same line
            before_comment = line.split('(*')[0].strip()
            
            # Try to extract parameter name from various patterns
            # Pattern 1: + paramName (* Question: ... *)
            param_match = re.search(r'\+\s*(\w+)\s*$', before_comment)
            if not param_match:
                # Pattern 2: | paramName (* Question: ... *)
                param_match = re.search(r'\|\s*(\w+)\s*$', before_comment)
            if not param_match:
                # Pattern 3: paramName = ... (* Question: ... *)
                param_match = re.search(r'^(\w+)\s*=', before_comment)
            if not param_match:
                # Pattern 4: Just paramName (* Question: ... *)
                param_match = re.search(r'(\w+)\s*$', before_comment)
                
            if param_match:
                param_name = param_match.group(1)
                questions[param_name] = question_text
                
    return questions

def strip_non_q_comments(text):
    """Remove all non-Question comments from EBNF text"""
    return re.sub(r'\(\*(?!\s*Question).*?\*\)', '', text, flags=re.S)

def split_productions(text):
    """Split EBNF text into individual productions"""
    prods = {}
    for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?);', text, flags=re.S):
        name, rhs = m.group(1), m.group(2).strip()
        prods[name] = rhs
    return prods

def strip_wrapping(s):
    """Strip unnecessary wrapping parentheses"""
    s = s.strip()
    if s.startswith('(') and s.endswith(')'):
        depth=0; ok=True
        for i,ch in enumerate(s):
            if ch=='(':
                depth+=1
            elif ch==')':
                depth-=1
                if depth==0 and i!=len(s)-1:
                    ok=False; break
        if ok: return s[1:-1].strip()
    return s

def split_top(s, sep):
    """Split string at top level (not inside parentheses)"""
    parts=[]; buf=[]; dep=0
    for ch in s:
        if ch in '([{': dep+=1
        elif ch in ')]}': dep-=1
        if ch==sep and dep==0:
            parts.append(''.join(buf).strip()); buf=[]
        else:
            buf.append(ch)
    if buf: parts.append(''.join(buf).strip())
    return [p for p in parts if p]

def token_name(part):
    """Extract token name from a part"""
    part = part.strip()
    m = re.fullmatch(r'\[\s*(.*?)\s*\]', part, flags=re.S)
    if m: part = m.group(1).strip()
    m = re.fullmatch(r'\{\s*(.*?)\s*\}', part, flags=re.S)
    if m: part = m.group(1).strip()
    
    alts = split_top(part, '|')
    if len(alts) > 1:
        for a in alts:
            a = a.strip()
            if not (a.startswith('"') and a.endswith('"')):
                return a
        return part
    
    seq = split_top(part, '+')
    if len(seq) > 1:
        return '+'.join([token_name(p) for p in seq])
    
    if part.startswith('"') and part.endswith('"'):
        return part.strip('"')
    
    return part

def expand(rhs, questions, prods):
    """Expand EBNF right-hand side into QA tree"""
    rhs = strip_wrapping(rhs.strip())

    # alternation
    alts = split_top(rhs, '|')
    if len(alts)>1:
        opts=[]
        for alt in alts:
            a = alt.strip()
            if a.startswith('"') and a.endswith('"'):
                opts.append({"answer": a.strip('"')})
            else:
                sub = expand(a, questions, prods)
                label = questions.get(a) or a
                opts.append({"answer": label, "follow_up": sub})
        return {"type":"choice", "question": questions.get(rhs) or "Choose an option", "options": opts}

    # sequence
    seq = split_top(rhs, '+')
    if len(seq)>1:
        # group question if exists for joined key
        joined = '+'.join([token_name(p) for p in seq])
        group_q = questions.get(joined)
        steps=[]
        for part in seq:
            sub = expand(part, questions, prods)
            if sub: steps.append(sub)
        return {"type":"sequence", "question": group_q or questions.get(rhs) or "Provide details", "steps": steps}

    # optional [ ]
    m = re.fullmatch(r'\[\s*(.*?)\s*\]', rhs, flags=re.S)
    if m:
        inner = expand(m.group(1), questions, prods)
        if inner: inner["optional"]=True
        return inner

    # repeat { }
    m = re.fullmatch(r'\{\s*(.*?)\s*\}', rhs, flags=re.S)
    if m:
        inner = expand(m.group(1), questions, prods)
        if inner: inner["repeatable"]=True
        return inner

    # group ( )
    m = re.fullmatch(r'\(\s*(.*?)\s*\)', rhs, flags=re.S)
    if m:
        return expand(m.group(1), questions, prods)

    # literal
    if rhs.startswith('"') and rhs.endswith('"'):
        return {"type":"field", "question": f'Enter {rhs.strip("\"")}', "field_type":"string"}

    # identifier
    ident = rhs.strip()
    if ident in prods:
        sub = expand(prods[ident], questions, prods)
        if sub and "question" not in sub and ident in questions:
            sub["question"] = questions[ident]
        return sub
    else:
        # terminal
        q = questions.get(ident) or f"Please provide {ident}"
        return {"type":"field", "question": q, "field_type":"string"}

def generate_qa_tree_for_endpoint(ebnf_path: str, endpoint_name: str) -> Dict[str, Any]:
    """Generate QA tree for a specific endpoint"""
    with open(ebnf_path, 'r') as f:
        text = f.read()
    
    # Extract questions and productions
    questions = extract_questions(text)
    cleaned = strip_non_q_comments(text)
    prods = split_productions(cleaned)
    
    # Find the endpoint production
    if endpoint_name not in prods:
        return None
    
    # Generate QA tree
    qa_tree = expand(prods[endpoint_name], questions, prods)
    
    # Find endpoint info from comments
    endpoint_pattern = rf'/\*\s*\n\s*Use Case \d+:.*?\n\s*Endpoint:\s*(.+?)\n.*?\*\)\s*\n{endpoint_name}\s*='
    endpoint_match = re.search(endpoint_pattern, text, re.MULTILINE | re.DOTALL)
    endpoint_path = endpoint_match.group(1).strip() if endpoint_match else f"/jobs/{endpoint_name}"
    
    return {
        "endpoint": endpoint_path,
        "use_case": endpoint_name,
        "qa_tree": qa_tree
    }

def walk_qa_tree(node, answers=None):
    """Walk through QA tree interactively and collect answers"""
    if answers is None:
        answers = {}
    
    if not node:
        return answers
    
    node_type = node.get("type")
    question = node.get("question", "Provide value")
    
    if node_type == "choice":
        # For UI, we return the structure instead of asking
        return {"type": "choice", "question": question, "options": node.get("options", [])}
        
    elif node_type == "sequence":
        # Process all steps
        steps = []
        for step in node.get("steps", []):
            step_result = walk_qa_tree(step, answers)
            if step_result:
                steps.append(step_result)
        return {"type": "sequence", "question": question, "steps": steps}
        
    elif node_type == "field":
        # Return field info for UI
        return {
            "type": "field",
            "question": question,
            "field_type": node.get("field_type", "string"),
            "optional": node.get("optional", False),
            "repeatable": node.get("repeatable", False)
        }
    
    return None