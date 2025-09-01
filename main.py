#!/usr/bin/env python3
"""
Health Plan Agent - Main Entry Point

A sophisticated multi-agent system for generating evidence-based health plans.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import Config
from src.utils.models import HealthPlanRequest
from src.agents.orchestrator_agent_fixed import OrchestratorAgentFixed
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import click

console = Console()

@click.command()
@click.option('--population', type=str, 
              default='postpartum_reconditioning', help='Target population (e.g., "senior_fitness", "athletes", "beginners")')
@click.option('--goals', multiple=True, type=str, 
              default=['core_restoration', 'pelvic_floor_recovery'], help='Health goals (e.g., "mobility", "strength", "weight_loss")')
@click.option('--constraints', multiple=True, default=['diastasis_recti'], 
              help='Health constraints or conditions')
@click.option('--timeline', default='12_weeks', help='Program timeline')
@click.option('--fitness-level', default='beginner', help='Fitness level')
@click.option('--preferences', multiple=True, default=[], help='User preferences')
@click.option('--output', default='health_plan.json', help='Output file path')
@click.option('--verbose', is_flag=True, help='Verbose output')
def main(population: str, goals: List[str], constraints: List[str], timeline: str, 
         fitness_level: str, preferences: List[str], output: str, verbose: bool):
    """Generate a comprehensive health plan using the multi-agent system."""
    
    console.print(Panel.fit(
        "[bold blue]Health Plan Agent[/bold blue]\n"
        "[italic]Evidence-based health plan generation system[/italic]",
        border_style="blue"
    ))
    
    # Validate configuration
    if not Config.validate():
        console.print("[red]Warning: Some API keys may not be configured[/red]")
    
    # Create health plan request
    try:
        request = HealthPlanRequest(
            population=population,
            goals=list(goals),
            constraints=list(constraints),
            timeline=timeline,
            fitness_level=fitness_level,
            preferences=list(preferences)
        )
    except ValueError as e:
        console.print(f"[red]Error: Invalid request parameters - {e}[/red]")
        return
    
    # Display request summary
    display_request_summary(request)
    
    # Generate health plan
    try:
        orchestrator = OrchestratorAgentFixed()
        health_plan = asyncio.run(orchestrator.generate_health_plan(request))
        
        # Save to file
        with open(output, 'w') as f:
            json.dump(health_plan, f, indent=2)
        
        console.print(f"\n[green]✅ Health plan saved to {output}[/green]")
        
        # Display summary
        display_plan_summary(health_plan, verbose)
        
    except Exception as e:
        console.print(f"[red]Error generating health plan: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())

def display_request_summary(request: HealthPlanRequest):
    """Display a summary of the health plan request."""
    
    table = Table(title="Health Plan Request")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Population", request.population)
    table.add_row("Goals", ", ".join(request.goals))
    table.add_row("Constraints", ", ".join(request.constraints))
    table.add_row("Timeline", request.timeline)
    table.add_row("Fitness Level", request.fitness_level)
    table.add_row("Preferences", ", ".join(request.preferences) if request.preferences else "None")
    
    console.print(table)

def display_plan_summary(health_plan: Dict[str, Any], verbose: bool):
    """Display a summary of the generated health plan."""
    
    plan_name = list(health_plan.keys())[0]
    plan_data = health_plan[plan_name]
    
    # Safety summary
    safety = plan_data.get("safety_protocols", {})
    safety_rating = safety.get("overall_safety", "unknown")
    validation_score = safety.get("validation_score", 0)
    
    # Component summary
    fitness = plan_data.get("fitness_component", {})
    nutrition = plan_data.get("nutrition_component", {})
    motivation = plan_data.get("motivation_component", {})
    
    table = Table(title="Generated Health Plan Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Details", style="white")
    
    table.add_row("Plan Name", plan_name)
    table.add_row("Safety Rating", safety_rating)
    table.add_row("Validation Score", f"{validation_score}/100")
    table.add_row("Fitness Days", str(len(fitness.get("exercises", {}))))
    table.add_row("Nutrition Goal", nutrition.get("goal", "N/A"))
    table.add_row("Motivation Elements", str(len(motivation.get("goal_setting", {}).get("primary_goals", []))))
    
    console.print(table)
    
    if verbose:
        # Display detailed components
        console.print("\n[bold]Detailed Components:[/bold]")
        
        # Fitness component
        if fitness.get("weekly_split"):
            console.print("\n[cyan]Weekly Split:[/cyan]")
            for day in fitness["weekly_split"]:
                console.print(f"  • {day}")
        
        # Nutrition component
        if nutrition.get("calories"):
            console.print(f"\n[cyan]Nutrition:[/cyan] {nutrition['calories']}")
        
        # Safety protocols
        if safety.get("safety_recommendations"):
            console.print("\n[cyan]Safety Recommendations:[/cyan]")
            for rec in safety["safety_recommendations"][:3]:  # Show first 3
                console.print(f"  • {rec}")

if __name__ == "__main__":
    main()

