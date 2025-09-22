#!/usr/bin/env python3
"""
Demo script showing how the C2M Endpoint Navigator works
"""

import json
import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Load the data
data_dir = Path("data")
with open(data_dir / "endpoints.json") as f:
    endpoints_data = json.load(f)
    endpoints = {ep["id"]: ep for ep in endpoints_data["endpoints"]}

with open(data_dir / "qa_tree.yaml") as f:
    qa_tree = yaml.safe_load(f)

# Demo scenarios
scenarios = [
    {
        "name": "Legal Firm - Certified Letters",
        "description": "Daily letters sent via Certified Mail with copies to legal representatives",
        "answers": {
            "docType": "single",
            "templateUsage": "yes",
            "recipientStyle": "template",
            "personalized": "yes"
        },
        "expected": "submitSingleDocTemplate"
    },
    {
        "name": "Monthly Invoices",
        "description": "End-of-month invoices, each in its own PDF with address in document",
        "answers": {
            "docType": "multi",
            "templateUsage": "no",
            "recipientStyle": "addressCapture",
            "personalized": "yes"
        },
        "expected": "submitMultiDoc"
    },
    {
        "name": "Medical Reports with Info Pages",
        "description": "Custom patient reports with standard medical information pages",
        "answers": {
            "docType": "merge",
            "templateUsage": "yes",
            "recipientStyle": "explicit",
            "personalized": "yes"
        },
        "expected": "submitMultiDocMerge"
    },
    {
        "name": "Combined Invoice PDF",
        "description": "All invoices in one big PDF that needs to be split",
        "answers": {
            "docType": "pdfSplit",
            "recipientStyle": "addressCapture"
        },
        "expected": "submitPdfSplit"
    }
]

def find_endpoint(answers):
    """Find matching endpoint based on answers"""
    for rule in qa_tree["endpoint_rules"]:
        matches = all(
            answers.get(field) == value
            for field, value in rule["conditions"].items()
        )
        if matches:
            return rule["endpoint"]
    return None

# Display header
console.print("\n[bold blue]🧭 C2M Endpoint Navigator - Demo Scenarios[/bold blue]\n")
console.print("This demo shows how the navigator recommends endpoints for common use cases.\n")

# Process each scenario
for i, scenario in enumerate(scenarios, 1):
    console.print(f"[bold cyan]Scenario {i}: {scenario['name']}[/bold cyan]")
    console.print(f"[dim]{scenario['description']}[/dim]\n")
    
    # Show answers
    console.print("[yellow]Answers:[/yellow]")
    for field, value in scenario['answers'].items():
        console.print(f"  • {field}: {value}")
    
    # Find endpoint
    endpoint_id = find_endpoint(scenario['answers'])
    
    if endpoint_id and endpoint_id == scenario['expected']:
        endpoint = endpoints[endpoint_id]
        
        # Create recommendation panel
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Endpoint", f"[bold green]{endpoint['method']} {endpoint['path']}[/bold green]")
        table.add_row("Description", endpoint['description'])
        
        console.print("\n", Panel(table, title="✅ Recommendation", border_style="green"))
    else:
        console.print(f"\n[red]❌ Error: Expected {scenario['expected']}, got {endpoint_id}[/red]")
    
    console.print("\n" + "─" * 80 + "\n")

# Show summary
console.print("[bold magenta]📊 Summary[/bold magenta]\n")
console.print("The C2M Endpoint Navigator helps developers choose from these endpoints:\n")

for ep_id, ep in endpoints.items():
    console.print(f"• [bold]{ep['path']}[/bold]")
    console.print(f"  {ep['description']}")
    console.print()

console.print("[dim]To run the interactive navigator:[/dim]")
console.print("• [cyan]Web Interface:[/cyan] streamlit run streamlit_app/app.py")
console.print("• [cyan]CLI Interface:[/cyan] python scripts/qa_recommender.py")
console.print("\n✨ The web interface at http://localhost:8501 is currently running!")