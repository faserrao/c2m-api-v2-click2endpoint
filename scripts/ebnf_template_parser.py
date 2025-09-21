"""
EBNF Template Parser for C2M API V2
Extracts template logic from commented EBNF blocks and generates appropriate UI flows
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
import json

@dataclass
class TemplateOption:
    """Represents one option in template logic"""
    from_template: List[str] = field(default_factory=list)  # What comes from template
    from_api: List[str] = field(default_factory=list)       # What must be provided in API
    requires_document_choice: bool = False                   # For Use Case 1 option 3
    
@dataclass
class EndpointTemplateLogic:
    """Template logic for an endpoint"""
    endpoint_name: str
    endpoint_path: str
    has_template_logic: bool
    options: List[TemplateOption] = field(default_factory=list)
    always_required: List[str] = field(default_factory=list)  # Always required regardless of template

@dataclass
class Parameter:
    """Parameter definition"""
    name: str
    question: str
    is_optional: bool = False
    is_repeatable: bool = False
    param_type: str = "string"

class EBNFTemplateParser:
    """Parser that understands template logic from EBNF comments"""
    
    def __init__(self, ebnf_file_path: str):
        self.ebnf_file_path = ebnf_file_path
        self.template_logic: Dict[str, EndpointTemplateLogic] = {}
        self.parameters: Dict[str, Parameter] = {}
        self.use_cases: Dict[str, Dict[str, Any]] = {}
        
    def parse(self):
        """Parse the EBNF file"""
        with open(self.ebnf_file_path, 'r') as f:
            content = f.read()
            
        # Extract use cases and their template logic
        self._extract_template_logic(content)
        
        # Extract parameter definitions and questions
        self._extract_parameters(content)
        
    def _extract_template_logic(self, content: str):
        """Extract template logic from commented TEMPLATE blocks"""
        # Pattern to find commented blocks with use case info and TEMPLATE - EBNF uses (* *) not /* */
        pattern = r'\(\*\s*\n?\s*Use Case (\d+):\s*(.*?)\n\s*Endpoint:\s*(.+?)\n(.*?)\*\)'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            case_num = match.group(1)
            description = match.group(2).strip()
            endpoint = match.group(3).strip()
            block_content = match.group(4)
            
            # Check if this block contains TEMPLATE logic
            if '"TEMPLATE"' in block_content:
                # Extract the production name
                prod_match = re.search(r'(\w+)\s*=', block_content)
                if prod_match:
                    prod_name = prod_match.group(1)
                    
                    # Parse the TEMPLATE alternations
                    logic = self._parse_template_alternations(prod_name, block_content)
                    logic.endpoint_path = endpoint
                    
                    self.template_logic[prod_name] = logic
                    
                    # Store use case info
                    self.use_cases[prod_name] = {
                        "case_num": case_num,
                        "description": description,
                        "endpoint": endpoint,
                        "has_template_logic": True
                    }
    
    def _parse_template_alternations(self, endpoint_name: str, block_content: str) -> EndpointTemplateLogic:
        """Parse TEMPLATE alternations to understand the logic"""
        logic = EndpointTemplateLogic(endpoint_name=endpoint_name, endpoint_path="", has_template_logic=True)
        
        # Extract the full production rule
        prod_pattern = rf'{endpoint_name}\s*=\s*([^;]+);'
        prod_match = re.search(prod_pattern, block_content, re.DOTALL)
        
        if not prod_match:
            return logic
            
        definition = prod_match.group(1).strip()
        
        # Special handling for mergeMultiDocWithTemplateParams
        if endpoint_name == "mergeMultiDocWithTemplateParams":
            # Parse: documentsToMerge + [ ("TEMPLATE" | recipientAddressSource) ] + ...
            # Extract the optional template choice
            opt_match = re.search(r'\[\s*\(\s*"TEMPLATE"\s*\|\s*(\w+)\s*\)\s*\]', definition)
            if opt_match:
                # Option 1: Template provides recipient
                option1 = TemplateOption(from_template=['recipient'], from_api=['documentsToMerge'])
                logic.options.append(option1)
                
                # Option 2: User provides recipient
                param_name = opt_match.group(1)
                option2 = TemplateOption(from_template=[], from_api=['documentsToMerge', param_name])
                logic.options.append(option2)
                
                # Extract always required (excluding the optional part)
                always_req = ['jobTemplate', 'paymentDetails']
                for req in always_req:
                    if req in definition:
                        logic.always_required.append(req)
                
                return logic
        
        # For submitSingleDocWithTemplateParams - parse the complex alternations
        parts = []
        depth = 0
        current = []
        i = 0
        
        # Find the main alternation group
        while i < len(definition):
            char = definition[i]
            if char == '(' and depth == 0 and not current:
                # Start of main group
                depth = 1
                i += 1
                group_content = []
                while i < len(definition) and depth > 0:
                    if definition[i] == '(':
                        depth += 1
                    elif definition[i] == ')':
                        depth -= 1
                    if depth > 0:
                        group_content.append(definition[i])
                    i += 1
                parts.append(('group', ''.join(group_content)))
            elif char == '+' and depth == 0:
                # Plus separator at top level
                if current:
                    parts.append(('item', ''.join(current).strip()))
                    current = []
                i += 1
            else:
                current.append(char)
                i += 1
        
        if current:
            parts.append(('item', ''.join(current).strip()))
        
        # Process the main alternation group
        for part_type, content in parts:
            if part_type == 'group':
                # This is our alternation group
                alternations = self._split_alternations(content)
                
                # Debug
                print(f"\nFound {len(alternations)} alternations for {endpoint_name}:")
                for i, alt in enumerate(alternations):
                    print(f"  Alt {i+1}: {alt}")
                
                for alt in alternations:
                    option = self._parse_single_alternation(alt)
                    logic.options.append(option)
            elif part_type == 'item' and content:
                # This is an always-required parameter
                param = self._extract_param_name(content)
                if param and param not in logic.always_required:
                    logic.always_required.append(param)
                
        return logic
    
    def _split_alternations(self, text: str) -> List[str]:
        """Split alternations by | at the top level"""
        alternations = []
        current = []
        depth = 0
        
        for char in text:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == '|' and depth == 0:
                alternations.append(''.join(current).strip())
                current = []
                continue
            current.append(char)
            
        if current:
            alternations.append(''.join(current).strip())
            
        return alternations
    
    def _parse_single_alternation(self, alt: str) -> TemplateOption:
        """Parse a single alternation to determine what comes from template vs API"""
        option = TemplateOption()
        
        # Check for TEMPLATE literal
        has_template = '"TEMPLATE"' in alt
        
        # Parse the structure
        if has_template:
            # Parse Use Case 1 alternations:
            # 1. ("TEMPLATE" | documentSourceIdentifier) + { recipientAddressSource }
            #    -> Template provides document, user provides recipients
            # 2. ("TEMPLATE" | { recipientAddressSource }) + documentSourceIdentifier  
            #    -> Template provides recipients, user provides document
            
            # Split by + to find parts
            parts = []
            depth = 0
            current = []
            for char in alt:
                if char == '+' and depth == 0:
                    parts.append(''.join(current).strip())
                    current = []
                else:
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        depth -= 1
                    current.append(char)
            if current:
                parts.append(''.join(current).strip())
            
            # Analyze each part
            template_provides = []
            api_provides = []
            
            for part in parts:
                if '"TEMPLATE"' in part and '|' in part:
                    # This is a choice between TEMPLATE and something else
                    # Extract what can be provided instead of TEMPLATE
                    non_template = part.replace('"TEMPLATE"', '').replace('|', '').replace('(', '').replace(')', '').strip()
                    param = self._extract_param_name(non_template)
                    
                    if param and 'document' in param.lower():
                        # ("TEMPLATE" | documentSourceIdentifier) means template CAN provide document
                        template_provides.append('document')
                    elif param and 'recipient' in param.lower():
                        # ("TEMPLATE" | recipientAddressSource) means template CAN provide recipients
                        template_provides.append('recipients')
                elif '"TEMPLATE"' not in part:
                    # This part must be provided by API
                    param = self._extract_param_name(part)
                    if param:
                        api_provides.append(param)
            
            # Set what template provides for this option
            option.from_template = template_provides
            option.from_api = api_provides
            
        else:
            # No TEMPLATE - everything must be provided
            # Parse: (documentSourceIdentifier + { recipientAddressSource})
            params = self._extract_all_params(alt)
            option.from_api.extend(params)
            
            # For Use Case 1, option 3 still needs to specify if document comes from template
            # This is a special case where job template can still provide the document
            # even though addresses don't come from template
            option.requires_document_choice = True
            
        return option
    
    def _extract_param_name(self, text: str) -> Optional[str]:
        """Extract parameter name from text"""
        text = text.strip()
        
        # Remove optional/repeatable markers
        if text.startswith('[') and text.endswith(']'):
            text = text[1:-1].strip()
        elif text.startswith('{') and text.endswith('}'):
            text = text[1:-1].strip()
            
        # Remove parentheses
        if text.startswith('(') and text.endswith(')'):
            text = text[1:-1].strip()
            
        # If it's a simple identifier, return it
        if re.match(r'^\w+$', text):
            return text
            
        return None
    
    def _extract_all_params(self, text: str) -> List[str]:
        """Extract all parameter names from text"""
        params = []
        
        # Remove outer parentheses if present
        text = text.strip()
        if text.startswith('(') and text.endswith(')'):
            text = text[1:-1].strip()
        
        # Handle sequences (split by +)
        parts = re.split(r'\s*\+\s*', text)
        
        for part in parts:
            param = self._extract_param_name(part)
            if param:
                params.append(param)
                
        return params
    
    def _extract_parameters(self, content: str):
        """Extract parameter definitions with questions from EBNF"""
        # Remove comments to get clean EBNF - EBNF uses (* *) not /* */
        clean_content = re.sub(r'\(\*.*?\*\)', '', content, flags=re.DOTALL)
        
        # Extract questions from comments first
        questions = {}
        lines = content.split('\n')
        
        for line in lines:
            # Look for inline questions
            q_match = re.search(r'\(\*\s*Question(?:\s*\(optional\))?\s*:\s*(.*?)\s*\*\)', line)
            if q_match:
                question_text = q_match.group(1).strip()
                # Find parameter name
                before_comment = line.split('(*')[0].strip()
                param_match = re.search(r'(\w+)\s*$', before_comment)
                if param_match:
                    param_name = param_match.group(1)
                    questions[param_name] = question_text
        
        # Extract parameter definitions
        param_pattern = r'^(\w+)\s*=\s*([^;]+);'
        
        for match in re.finditer(param_pattern, clean_content, re.MULTILINE):
            param_name = match.group(1)
            definition = match.group(2).strip()
            
            # Skip if it's a use case (not a simple parameter)
            if param_name in self.use_cases:
                continue
                
            # Determine if optional/repeatable
            is_optional = definition.startswith('[') or '?' in definition
            is_repeatable = definition.startswith('{') or '+' in definition or '*' in definition
            
            # Get question
            question = questions.get(param_name, f"Please provide {param_name}")
            
            # Determine type
            param_type = self._infer_param_type(param_name, definition)
            
            self.parameters[param_name] = Parameter(
                name=param_name,
                question=question,
                is_optional=is_optional,
                is_repeatable=is_repeatable,
                param_type=param_type
            )
    
    def _infer_param_type(self, name: str, definition: str) -> str:
        """Infer parameter type from name and definition"""
        name_lower = name.lower()
        def_lower = definition.lower()
        
        if 'address' in name_lower and 'recipient' in name_lower:
            return 'address'
        elif 'email' in name_lower:
            return 'email'
        elif 'url' in name_lower:
            return 'url'
        elif 'id' in name_lower or definition.strip() == 'id':
            return 'id'
        elif 'number' in def_lower or 'integer' in def_lower:
            return 'number'
        elif '|' in definition:
            return 'choice'
        else:
            return 'string'
    
    def generate_ui_flow(self, endpoint_name: str) -> Dict[str, Any]:
        """Generate UI flow for an endpoint"""
        # Check if this endpoint has template logic
        if endpoint_name in self.template_logic:
            return self._generate_template_ui_flow(endpoint_name)
        else:
            return self._generate_standard_ui_flow(endpoint_name)
    
    def _generate_template_ui_flow(self, endpoint_name: str) -> Dict[str, Any]:
        """Generate UI flow for endpoints with template logic"""
        logic = self.template_logic[endpoint_name]
        
        flow = {
            "endpoint": logic.endpoint_path,
            "has_template_logic": True,
            "questions": []
        }
        
        # First question: determine what comes from template
        first_q = {
            "id": "template_choice",
            "type": "choice",
            "question": "What information will come from the template?",
            "options": []
        }
        
        # Build options based on template logic
        for i, option in enumerate(logic.options):
            opt_data = {
                "value": f"option_{i}",
                "from_template": option.from_template,
                "from_api": option.from_api,
                "requires_document_choice": option.requires_document_choice
            }
            
            if option.from_template:
                label = f"Template provides: {', '.join(option.from_template)}"
                if option.from_api:
                    label += f" (you provide: {', '.join(option.from_api)})"
            else:
                label = "Template provides: job options only"
                if option.from_api:
                    label += f" (you provide: {', '.join(option.from_api)})"
                
            opt_data["label"] = label
            first_q["options"].append(opt_data)
        
        flow["questions"].append(first_q)
        
        # Add always required parameters
        for param in logic.always_required:
            if param in self.parameters:
                p = self.parameters[param]
                flow["questions"].append({
                    "id": param,
                    "type": p.param_type,
                    "question": p.question,
                    "required": not p.is_optional,
                    "repeatable": p.is_repeatable
                })
        
        return flow
    
    def _generate_standard_ui_flow(self, endpoint_name: str) -> Dict[str, Any]:
        """Generate standard UI flow for endpoints without template logic"""
        # This would parse the regular EBNF definition
        # For now, return a simple structure
        return {
            "endpoint": endpoint_name,
            "has_template_logic": False,
            "questions": []
        }