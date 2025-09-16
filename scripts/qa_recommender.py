#!/usr/bin/env python3
"""
Click2Endpoint CLI - C2M API v2
Interactive questionnaire to help developers find the right C2M API endpoint
"""

import json
import yaml
import questionary
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import csv
import jsonlines
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

class EndpointNavigator:
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        
        self.data_dir = data_dir
        self.endpoints = self._load_endpoints()
        self.qa_tree = self._load_qa_tree()
        self.answers = {}
        self.session_log = []
    
    def _load_endpoints(self) -> Dict[str, Any]:
        """Load endpoint metadata from JSON file"""
        with open(self.data_dir / "endpoints.json", "r") as f:
            data = json.load(f)
            return {ep["id"]: ep for ep in data["endpoints"]}
    
    def _load_qa_tree(self) -> Dict[str, Any]:
        """Load QA decision tree from YAML file"""
        with open(self.data_dir / "qa_tree.yaml", "r") as f:
            return yaml.safe_load(f)
    
    def run_questionnaire(self) -> Optional[str]:
        """Run the interactive questionnaire and return recommended endpoint ID"""
        console.print("\n[bold blue]🎯 Welcome to Click2Endpoint - C2M API v2![/bold blue]")
        console.print("Answer a few questions to find the perfect API endpoint for your use case.\n")
        
        # Process each tier of questions
        for tier in self.qa_tree["decision_tree"]:
            # Check if this question should be asked based on conditions
            if "conditions" in tier:
                should_ask = all(
                    self.answers.get(field) in values
                    for field, values in tier["conditions"].items()
                )
                if not should_ask:
                    continue
            
            # Skip optional questions if not needed
            if tier.get("optional", False):
                if not questionary.confirm(
                    f"Would you like to specify {tier['question'].lower()}?",
                    default=False
                ).ask():
                    continue
            
            # Build choices for the question
            choices = []
            for option in tier["options"]:
                choice_text = f"{option['label']}"
                if "description" in option:
                    choice_text += f" - {option['description']}"
                choices.append(questionary.Choice(choice_text, value=option["value"]))
            
            # Ask the question
            if tier.get("multiselect", False):
                answer = questionary.checkbox(
                    tier["question"],
                    choices=choices
                ).ask()
            else:
                answer = questionary.select(
                    tier["question"],
                    choices=choices
                ).ask()
            
            if answer is None:  # User cancelled
                return None
            
            self.answers[tier["field"]] = answer
            self.session_log.append({
                "tier": tier.get("tier", "unknown"),
                "question": tier["question"],
                "answer": answer
            })
        
        # Find matching endpoint
        endpoint_id = self._find_matching_endpoint()
        
        if endpoint_id:
            self._display_recommendation(endpoint_id)
            self._log_session(endpoint_id)
            
            # Ask if user wants to export the session
            if questionary.confirm("\nWould you like to save this recommendation session?", default=True).ask():
                self._export_session(endpoint_id)
        else:
            console.print("\n[red]❌ No matching endpoint found for your criteria.[/red]")
            console.print("Please check your answers or contact support.")
        
        return endpoint_id
    
    def _find_matching_endpoint(self) -> Optional[str]:
        """Find endpoint that matches the given answers"""
        for rule in self.qa_tree["endpoint_rules"]:
            matches = all(
                self.answers.get(field) == value
                for field, value in rule["conditions"].items()
            )
            if matches:
                return rule["endpoint"]
        return None
    
    def _display_recommendation(self, endpoint_id: str):
        """Display the recommended endpoint with details"""
        endpoint = self.endpoints[endpoint_id]
        
        # Create recommendation panel
        console.print("\n[bold green]✅ Recommended Endpoint Found![/bold green]\n")
        
        # Endpoint details table
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Endpoint", f"[bold]{endpoint['method']} {endpoint['path']}[/bold]")
        table.add_row("Description", endpoint['description'])
        if endpoint.get('docPath'):
            doc_url = f"http://localhost:4000{endpoint['docPath']}"
            table.add_row("Documentation", f"[link={doc_url}]{doc_url}[/link]")
        
        if endpoint.get("useCases"):
            table.add_row("Use Cases", "\n".join(f"• {uc}" for uc in endpoint['useCases']))
        
        console.print(Panel(table, title="Endpoint Details", border_style="green"))
        
        # Show example if available
        if endpoint.get("example"):
            console.print("\n[cyan]📋 Example Code:[/cyan]")
            console.print(f"[bold]{endpoint['example']['description']}[/bold]\n")
            syntax = Syntax(endpoint['example']['code'], "bash", theme="monokai", line_numbers=True)
            console.print(syntax)
            console.print("\n[yellow]💡 Remember to replace YOUR_CLIENT_ID and YOUR_SECRET with your actual credentials[/yellow]")
    
    def _log_session(self, endpoint_id: str):
        """Log the session for training data"""
        timestamp = datetime.now().isoformat()
        endpoint = self.endpoints[endpoint_id]
        
        # Prepare log entry
        log_entry = {
            "timestamp": timestamp,
            "session_log": self.session_log,
            "answers": self.answers,
            "recommended_endpoint": endpoint["path"],
            "endpoint_id": endpoint_id
        }
        
        # Append to JSONL file
        log_file = self.data_dir.parent / "logs" / "sessions.jsonl"
        log_file.parent.mkdir(exist_ok=True)
        
        with jsonlines.open(log_file, mode="a") as writer:
            writer.write(log_entry)
        
        # Also append to CSV for simple analysis
        csv_file = self.data_dir.parent / "logs" / "recommendations.csv"
        csv_exists = csv_file.exists()
        
        with open(csv_file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "timestamp", "docType", "templateUsage", "endpoint", "endpoint_id"
            ])
            if not csv_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": timestamp,
                "docType": self.answers.get("docType", ""),
                "templateUsage": self.answers.get("templateUsage", ""),
                "endpoint": endpoint["path"],
                "endpoint_id": endpoint_id
            })
    
    def _export_session(self, endpoint_id: str):
        """Export session data for user"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "questions_and_answers": self.session_log,
            "final_answers": self.answers,
            "recommendation": {
                "endpoint_id": endpoint_id,
                "endpoint": self.endpoints[endpoint_id]["path"],
                "description": self.endpoints[endpoint_id]["description"]
            }
        }
        
        # Ask format preference
        format_choice = questionary.select(
            "Export format:",
            choices=["JSON", "YAML", "Both"]
        ).ask()
        
        if format_choice in ["JSON", "Both"]:
            filename = f"c2m_recommendation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
            console.print(f"[green]✓ Saved to {filename}[/green]")
        
        if format_choice in ["YAML", "Both"]:
            filename = f"c2m_recommendation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            with open(filename, "w") as f:
                yaml.dump(export_data, f, default_flow_style=False)
            console.print(f"[green]✓ Saved to {filename}[/green]")

def main():
    """Main CLI entry point"""
    navigator = EndpointNavigator()
    
    while True:
        navigator.answers = {}  # Reset for new session
        navigator.session_log = []
        
        endpoint_id = navigator.run_questionnaire()
        
        if not questionary.confirm("\nWould you like to find another endpoint?", default=False).ask():
            console.print("\n[blue]Thanks for using Click2Endpoint! 🚀[/blue]")
            break

if __name__ == "__main__":
    main()