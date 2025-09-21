"""
EBNF Parser Module for C2M API V2
Parses EBNF grammar with embedded questions to generate dynamic Q&A trees for Level 2 (parameter collection)
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json

@dataclass
class Question:
    """Represents a question extracted from EBNF comments"""
    field_name: str
    question_text: str
    is_optional: bool = False
    is_repeatable: bool = False
    
@dataclass
class UseCase:
    """Represents a use case definition from EBNF"""
    name: str
    endpoint: str
    description: str
    question: str
    ebnf_definition: str
    parameters: List[str] = field(default_factory=list)
    
@dataclass
class Parameter:
    """Represents a parameter with its question"""
    name: str
    question: str
    is_optional: bool = False
    is_repeatable: bool = False
    choices: List[str] = field(default_factory=list)

class EBNFParser:
    """Parser for EBNF with embedded questions"""
    
    def __init__(self, ebnf_file_path: str):
        self.ebnf_file_path = ebnf_file_path
        self.use_cases: Dict[str, UseCase] = {}
        self.parameters: Dict[str, Parameter] = {}
        self.questions: Dict[str, str] = {}
        
    def parse(self):
        """Parse the EBNF file and extract use cases and questions"""
        with open(self.ebnf_file_path, 'r') as f:
            content = f.read()
            
        # Extract use cases
        self._extract_use_cases(content)
        
        # Extract parameter questions
        self._extract_questions(content)
        
        # Extract parameter definitions
        self._extract_parameters(content)
        
    def _extract_use_cases(self, content: str):
        """Extract use case definitions from EBNF"""
        # Pattern to match use case blocks with comments
        use_case_pattern = r'\(\*\s*\n\s*Use Case (\d+):\s*(.+?)\n\s*Endpoint:\s*(.+?)\n(?:\s*Question:\s*(.+?)\n)?\s*\*\)\s*\n(\w+)\s*='
        
        matches = re.finditer(use_case_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            case_num = match.group(1)
            description = match.group(2).strip()
            endpoint = match.group(3).strip()
            question = match.group(4).strip() if match.group(4) else ""
            param_name = match.group(5)
            
            # Extract the full EBNF definition
            definition_pattern = rf'{param_name}\s*=\s*([^;]+);'
            def_match = re.search(definition_pattern, content, re.MULTILINE | re.DOTALL)
            
            if def_match:
                ebnf_def = def_match.group(1).strip()
                
                # Extract referenced parameters
                params = self._extract_referenced_params(ebnf_def)
                
                self.use_cases[param_name] = UseCase(
                    name=param_name,
                    endpoint=endpoint,
                    description=description,
                    question=question,
                    ebnf_definition=ebnf_def,
                    parameters=params
                )
    
    def _extract_questions(self, content: str):
        """Extract inline questions from EBNF comments"""
        # Pattern to match inline questions: (* Question: ... *)
        question_pattern = r'\(\*\s*Question(?:\s*\(optional\))?\s*:\s*(.+?)\s*\*\)'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '(*' in line and 'Question' in line:
                match = re.search(question_pattern, line)
                if match:
                    question_text = match.group(1).strip()
                    
                    # Look for the parameter name before the question
                    before_comment = line.split('(*')[0].strip()
                    
                    # Extract parameter name
                    param_match = re.search(r'(\w+)\s*$', before_comment)
                    if param_match:
                        param_name = param_match.group(1)
                        self.questions[param_name] = question_text
                        
    def _extract_referenced_params(self, ebnf_def: str) -> List[str]:
        """Extract parameter names referenced in an EBNF definition"""
        # Remove inline comments first
        clean_def = re.sub(r'\(\*[^*]*\*\)', '', ebnf_def)
        
        # Pattern to match parameter references (camelCase identifiers)
        param_pattern = r'\b([a-z][a-zA-Z0-9]*)\b'
        
        # Keywords to exclude
        keywords = {'TEMPLATE', 'integer', 'string'}
        
        params = []
        for match in re.finditer(param_pattern, clean_def):
            param = match.group(1)
            # Check if it looks like a parameter name (camelCase or lowercase)
            if param not in keywords and param not in params and len(param) > 3:
                params.append(param)
                
        return params
    
    def _extract_parameters(self, content: str):
        """Extract parameter definitions from EBNF"""
        # Pattern to match parameter definitions
        param_pattern = r'^(\w+)\s*=\s*([^;]+);'
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('(*'):
                i += 1
                continue
                
            # Check for parameter definition
            match = re.match(param_pattern, line)
            if match:
                param_name = match.group(1)
                definition = match.group(2).strip()
                
                # Skip if it's a use case (already processed)
                if param_name not in self.use_cases:
                    # Check for question on same line
                    question = self.questions.get(param_name, f"Please provide {param_name}")
                    
                    # Determine if optional/repeatable
                    is_optional = definition.startswith('[') or '?' in definition
                    is_repeatable = definition.startswith('{') or '+' in definition or '*' in definition
                    
                    # Extract choices if it's an alternation
                    choices = []
                    if '|' in definition:
                        # Simple alternation pattern
                        choice_pattern = r'"([^"]+)"'
                        choices = re.findall(choice_pattern, definition)
                    
                    self.parameters[param_name] = Parameter(
                        name=param_name,
                        question=question,
                        is_optional=is_optional,
                        is_repeatable=is_repeatable,
                        choices=choices
                    )
            
            i += 1
    
    def get_use_cases(self) -> List[UseCase]:
        """Get all parsed use cases"""
        return list(self.use_cases.values())
    
    def get_use_case_by_endpoint(self, endpoint: str) -> Optional[UseCase]:
        """Get use case by endpoint path"""
        for use_case in self.use_cases.values():
            if endpoint in use_case.endpoint:
                return use_case
        return None
    
    def get_parameter_questions(self, use_case_name: str) -> List[Parameter]:
        """Get all parameter questions for a use case"""
        if use_case_name not in self.use_cases:
            return []
            
        use_case = self.use_cases[use_case_name]
        questions = []
        
        for param in use_case.parameters:
            if param in self.parameters:
                questions.append(self.parameters[param])
                
        return questions
    
    def generate_qa_tree(self, use_case_name: str) -> Dict[str, Any]:
        """Generate a Q&A tree for a specific use case"""
        if use_case_name not in self.use_cases:
            return {}
            
        use_case = self.use_cases[use_case_name]
        
        tree = {
            "use_case": use_case.name,
            "endpoint": use_case.endpoint,
            "description": use_case.description,
            "initial_question": use_case.question,
            "parameters": []
        }
        
        for param in use_case.parameters:
            if param in self.parameters:
                param_obj = self.parameters[param]
                tree["parameters"].append({
                    "name": param_obj.name,
                    "question": param_obj.question,
                    "optional": param_obj.is_optional,
                    "repeatable": param_obj.is_repeatable,
                    "choices": param_obj.choices
                })
                
        return tree