"""
Simple EBNF Parser for C2M API V2
Parses EBNF with embedded questions without recursion issues
"""

import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import json

@dataclass
class EBNFProduction:
    """Represents an EBNF production rule"""
    name: str
    definition: str
    question: Optional[str] = None
    is_optional: bool = False
    is_repeatable: bool = False

class SimpleEBNFParser:
    """A simpler EBNF parser that avoids infinite recursion"""
    
    def __init__(self, ebnf_file_path: str):
        self.ebnf_file_path = ebnf_file_path
        self.productions: Dict[str, EBNFProduction] = {}
        self.use_cases: Dict[str, Dict[str, Any]] = {}
        self._visited: Set[str] = set()  # Track visited nodes to prevent recursion
        
    def parse(self):
        """Parse the EBNF file"""
        with open(self.ebnf_file_path, 'r') as f:
            content = f.read()
            
        # Extract use cases with their metadata
        self._extract_use_cases(content)
        
        # Extract all productions with their questions
        self._extract_productions(content)
        
    def _extract_use_cases(self, content: str):
        """Extract use case definitions from EBNF"""
        # Pattern to match use case blocks
        pattern = r'\(\*\s*\n\s*Use Case (\d+):\s*(.+?)\n\s*Endpoint:\s*(.+?)\n(?:\s*Question:\s*(.+?)\n)?\s*\*\)\s*\n(\w+)\s*='
        
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            case_num = match.group(1)
            description = match.group(2).strip()
            endpoint = match.group(3).strip()
            question = match.group(4).strip() if match.group(4) else ""
            param_name = match.group(5)
            
            self.use_cases[param_name] = {
                "case_num": case_num,
                "description": description,
                "endpoint": endpoint,
                "question": question,
                "name": param_name
            }
    
    def _extract_productions(self, content: str):
        """Extract all production rules with their questions"""
        # First, extract inline questions for each line
        questions = {}
        lines = content.split('\n')
        
        for line in lines:
            # Match inline questions: (* Question: ... *) or (* Question (optional): ... *)
            q_match = re.search(r'\(\*\s*Question(?:\s*\(optional\))?\s*:\s*(.*?)\s*\*\)', line)
            if q_match:
                question_text = q_match.group(1).strip()
                
                # Find the parameter name before the question
                before_comment = line.split('(*')[0].strip()
                
                # Try different patterns to find parameter name
                param_name = None
                
                # Pattern: + paramName (* Question: ... *)
                if not param_name:
                    m = re.search(r'\+\s*(\w+)\s*$', before_comment)
                    if m: param_name = m.group(1)
                
                # Pattern: | paramName (* Question: ... *)
                if not param_name:
                    m = re.search(r'\|\s*(\w+)\s*$', before_comment)
                    if m: param_name = m.group(1)
                
                # Pattern: paramName = ... (* Question: ... *)
                if not param_name:
                    m = re.search(r'^(\w+)\s*=', before_comment)
                    if m: param_name = m.group(1)
                
                # Pattern: just paramName (* Question: ... *)
                if not param_name:
                    m = re.search(r'(\w+)\s*$', before_comment)
                    if m: param_name = m.group(1)
                
                if param_name:
                    questions[param_name] = question_text
        
        # Now extract production rules
        # Pattern: name = definition ;
        prod_pattern = r'^(\w+)\s*=\s*([^;]+);'
        
        # Process the content to extract productions
        content_without_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        for match in re.finditer(prod_pattern, content_without_comments, re.MULTILINE):
            name = match.group(1)
            definition = match.group(2).strip()
            
            # Create production
            prod = EBNFProduction(
                name=name,
                definition=definition,
                question=questions.get(name)
            )
            
            # Check if optional or repeatable
            if definition.startswith('[') and definition.endswith(']'):
                prod.is_optional = True
                prod.definition = definition[1:-1].strip()
            elif definition.startswith('{') and definition.endswith('}'):
                prod.is_repeatable = True
                prod.definition = definition[1:-1].strip()
                
            self.productions[name] = prod
    
    def get_use_case_parameters(self, use_case_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Get parameters for a use case with their questions"""
        if use_case_name not in self.productions:
            return []
            
        self._visited.clear()
        parameters = []
        
        # Start with the use case production
        prod = self.productions[use_case_name]
        self._expand_production(prod, parameters, 0, max_depth)
        
        return parameters
    
    def _expand_production(self, prod: EBNFProduction, parameters: List[Dict[str, Any]], depth: int, max_depth: int):
        """Expand a production rule to find all parameters"""
        if depth > max_depth or prod.name in self._visited:
            return
            
        self._visited.add(prod.name)
        
        # If this production has a question, it's a parameter we need to collect
        if prod.question:
            param_info = {
                "name": prod.name,
                "question": prod.question,
                "optional": prod.is_optional,
                "repeatable": prod.is_repeatable
            }
            
            # Try to determine the type based on the definition
            param_info["type"] = self._infer_type(prod)
            
            parameters.append(param_info)
        
        # Parse the definition to find referenced productions
        # Handle sequences (separated by +)
        parts = re.split(r'\s*\+\s*', prod.definition)
        
        for part in parts:
            part = part.strip()
            
            # Handle alternations (separated by |)
            if '|' in part:
                choices = re.split(r'\s*\|\s*', part)
                choice_info = {
                    "name": f"{prod.name}_choice",
                    "question": prod.question or f"Choose option for {prod.name}",
                    "type": "choice",
                    "choices": []
                }
                
                for choice in choices:
                    choice = choice.strip()
                    # Remove parentheses
                    if choice.startswith('(') and choice.endswith(')'):
                        choice = choice[1:-1].strip()
                    
                    # Check if it's a literal
                    if choice.startswith('"') and choice.endswith('"'):
                        choice_info["choices"].append(choice.strip('"'))
                    else:
                        choice_info["choices"].append(choice)
                        # If it's a reference, expand it
                        if choice in self.productions:
                            self._expand_production(self.productions[choice], parameters, depth + 1, max_depth)
                
                if len(choice_info["choices"]) > 0 and prod.question:
                    parameters.append(choice_info)
            else:
                # Handle single references
                # Remove optional/repeatable markers
                if part.startswith('[') and part.endswith(']'):
                    part = part[1:-1].strip()
                elif part.startswith('{') and part.endswith('}'):
                    part = part[1:-1].strip()
                
                # Remove parentheses
                if part.startswith('(') and part.endswith(')'):
                    part = part[1:-1].strip()
                
                # Check if it's a production reference
                if part in self.productions:
                    self._expand_production(self.productions[part], parameters, depth + 1, max_depth)
    
    def _infer_type(self, prod: EBNFProduction) -> str:
        """Infer the parameter type from its definition"""
        definition = prod.definition.lower()
        
        if 'address' in prod.name.lower():
            return 'address'
        elif 'email' in definition or 'email' in prod.name.lower():
            return 'email'
        elif 'url' in definition or 'url' in prod.name.lower():
            return 'url'
        elif 'number' in definition or 'integer' in definition:
            return 'number'
        elif 'card' in prod.name.lower() and 'credit' in prod.name.lower():
            return 'credit_card'
        elif '|' in prod.definition:
            return 'choice'
        elif prod.is_repeatable:
            return 'list'
        else:
            return 'text'
    
    def generate_parameter_flow(self, use_case_name: str) -> Dict[str, Any]:
        """Generate a parameter collection flow for a use case"""
        use_case = self.use_cases.get(use_case_name, {})
        parameters = self.get_use_case_parameters(use_case_name)
        
        return {
            "use_case": use_case_name,
            "endpoint": use_case.get("endpoint", ""),
            "description": use_case.get("description", ""),
            "parameters": parameters
        }