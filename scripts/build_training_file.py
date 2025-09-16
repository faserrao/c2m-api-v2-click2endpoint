#!/usr/bin/env python3
"""
Build training data files for LLM fine-tuning from logged recommendation sessions
Supports multiple output formats: OpenAI, Claude, generic JSONL
"""

import json
import jsonlines
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import yaml

class TrainingDataBuilder:
    def __init__(self, input_file: Path, output_file: Path, format: str = "openai"):
        self.input_file = input_file
        self.output_file = output_file
        self.format = format
        self.sessions = self._load_sessions()
        
    def _load_sessions(self) -> List[Dict[str, Any]]:
        """Load all sessions from JSONL file"""
        sessions = []
        with jsonlines.open(self.input_file) as reader:
            for obj in reader:
                sessions.append(obj)
        return sessions
    
    def build_training_data(self):
        """Build training data in the specified format"""
        if self.format == "openai":
            self._build_openai_format()
        elif self.format == "claude":
            self._build_claude_format()
        elif self.format == "generic":
            self._build_generic_format()
        else:
            raise ValueError(f"Unsupported format: {self.format}")
    
    def _build_openai_format(self):
        """Build training data in OpenAI fine-tuning format"""
        training_data = []
        
        for session in self.sessions:
            # Build the user prompt from Q&A session
            user_prompt = self._build_user_prompt(session)
            
            # Build the assistant response
            assistant_response = self._build_assistant_response(session)
            
            training_example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a C2M API endpoint recommendation assistant. Based on the user's requirements, recommend the most appropriate API endpoint for document submission."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    },
                    {
                        "role": "assistant",
                        "content": assistant_response
                    }
                ]
            }
            
            training_data.append(training_example)
        
        # Write to file
        with jsonlines.open(self.output_file, mode="w") as writer:
            for example in training_data:
                writer.write(example)
        
        print(f"✅ Created {len(training_data)} training examples in OpenAI format")
    
    def _build_claude_format(self):
        """Build training data in Claude/Anthropic format"""
        training_data = []
        
        for session in self.sessions:
            user_prompt = self._build_user_prompt(session)
            assistant_response = self._build_assistant_response(session)
            
            training_example = {
                "prompt": f"\n\nHuman: {user_prompt}\n\nAssistant: {assistant_response}",
                "metadata": {
                    "endpoint": session["recommended_endpoint"],
                    "timestamp": session["timestamp"]
                }
            }
            
            training_data.append(training_example)
        
        with jsonlines.open(self.output_file, mode="w") as writer:
            for example in training_data:
                writer.write(example)
        
        print(f"✅ Created {len(training_data)} training examples in Claude format")
    
    def _build_generic_format(self):
        """Build training data in generic JSONL format"""
        training_data = []
        
        for session in self.sessions:
            training_example = {
                "input": self._build_user_prompt(session),
                "output": self._build_assistant_response(session),
                "metadata": {
                    "answers": session["answers"],
                    "endpoint": session["recommended_endpoint"],
                    "endpoint_id": session.get("endpoint_id", ""),
                    "timestamp": session["timestamp"]
                }
            }
            
            training_data.append(training_example)
        
        with jsonlines.open(self.output_file, mode="w") as writer:
            for example in training_data:
                writer.write(example)
        
        print(f"✅ Created {len(training_data)} training examples in generic format")
    
    def _build_user_prompt(self, session: Dict[str, Any]) -> str:
        """Build a natural language prompt from session data"""
        answers = session["answers"]
        
        # Map technical answers to natural language
        prompt_parts = []
        
        if "docType" in answers:
            doc_type_map = {
                "single": "I need to submit a single document",
                "multi": "I need to submit multiple separate documents",
                "merge": "I need to submit multiple documents that should be merged together",
                "pdfSplit": "I have a single PDF containing multiple documents that need to be split"
            }
            prompt_parts.append(doc_type_map.get(answers["docType"], ""))
        
        if "templateUsage" in answers:
            if answers["templateUsage"] == "yes":
                prompt_parts.append("I want to use a saved job template")
            else:
                prompt_parts.append("I'll configure the job parameters manually")
        
        if "recipientStyle" in answers:
            recipient_map = {
                "explicit": "The recipient addresses will be provided in the API call",
                "template": "The recipient addresses are saved in a template/mailing list",
                "addressCapture": "The addresses should be extracted from the document content"
            }
            prompt_parts.append(recipient_map.get(answers["recipientStyle"], ""))
        
        if "personalized" in answers:
            if answers["personalized"] == "yes":
                prompt_parts.append("Each document is personalized for its recipient")
            else:
                prompt_parts.append("The same document content goes to all recipients")
        
        if "extraFeatures" in answers and answers["extraFeatures"]:
            features = answers["extraFeatures"]
            if isinstance(features, list) and features:
                feature_text = "I need these features: " + ", ".join(features)
                prompt_parts.append(feature_text)
        
        return ". ".join(filter(None, prompt_parts)) + ". Which C2M API endpoint should I use?"
    
    def _build_assistant_response(self, session: Dict[str, Any]) -> str:
        """Build the assistant's response recommending the endpoint"""
        endpoint = session["recommended_endpoint"]
        endpoint_id = session.get("endpoint_id", "")
        
        # Load endpoint details
        endpoints_file = Path(__file__).parent.parent / "data" / "endpoints.json"
        with open(endpoints_file) as f:
            endpoints_data = json.load(f)
            endpoint_details = None
            for ep in endpoints_data["endpoints"]:
                if ep["id"] == endpoint_id:
                    endpoint_details = ep
                    break
        
        response_parts = [
            f"Based on your requirements, I recommend using the **{endpoint}** endpoint."
        ]
        
        if endpoint_details:
            response_parts.append(f"\n\n{endpoint_details['description']}")
            
            if endpoint_details.get("useCases"):
                response_parts.append("\n\nThis endpoint is commonly used for:")
                for uc in endpoint_details["useCases"]:
                    response_parts.append(f"- {uc}")
            
            if endpoint_details.get("docPath"):
                response_parts.append(f"\n\nFor detailed documentation, see the endpoint documentation")
        
        return "\n".join(response_parts)
    
    def generate_statistics(self):
        """Generate statistics about the training data"""
        stats = {
            "total_sessions": len(self.sessions),
            "endpoint_distribution": {},
            "answer_patterns": {}
        }
        
        for session in self.sessions:
            endpoint = session["recommended_endpoint"]
            stats["endpoint_distribution"][endpoint] = stats["endpoint_distribution"].get(endpoint, 0) + 1
            
            for field, value in session["answers"].items():
                if field not in stats["answer_patterns"]:
                    stats["answer_patterns"][field] = {}
                stats["answer_patterns"][field][str(value)] = stats["answer_patterns"][field].get(str(value), 0) + 1
        
        # Save statistics
        stats_file = self.output_file.with_suffix(".stats.json")
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n📊 Training Data Statistics:")
        print(f"Total sessions: {stats['total_sessions']}")
        print("\nEndpoint distribution:")
        for endpoint, count in sorted(stats["endpoint_distribution"].items(), key=lambda x: x[1], reverse=True):
            print(f"  {endpoint}: {count} ({count/stats['total_sessions']*100:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description="Build LLM training data from C2M Navigator sessions")
    parser.add_argument("--input", type=Path, default="logs/sessions.jsonl",
                        help="Input JSONL file with session logs")
    parser.add_argument("--output", type=Path, default="training_data.jsonl",
                        help="Output file for training data")
    parser.add_argument("--format", choices=["openai", "claude", "generic"], default="openai",
                        help="Output format for training data")
    parser.add_argument("--stats", action="store_true",
                        help="Generate statistics about the training data")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not args.input.exists():
        print(f"❌ Input file not found: {args.input}")
        print("Make sure you have some logged sessions first.")
        return
    
    # Create output directory if needed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Build training data
    builder = TrainingDataBuilder(args.input, args.output, args.format)
    builder.build_training_data()
    
    # Generate statistics if requested
    if args.stats:
        builder.generate_statistics()
    
    print(f"\n✨ Training data saved to: {args.output}")

if __name__ == "__main__":
    main()