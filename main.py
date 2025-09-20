"""Command-line interface for the AI-powered debugger."""

import os
import sys
import json
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.debugger import AIDebugger

console = Console()


@click.group()
@click.option('--project-path', '-p', default='.', help='Path to the project to analyze')
@click.option('--api-key', '-k', envvar='GEMINI_API_KEY', help='Gemini API key')
@click.pass_context
def cli(ctx, project_path, api_key):
    """AI-Powered Debugger - Semantic code analysis and bug fixing."""
    ctx.ensure_object(dict)
    ctx.obj['project_path'] = os.path.abspath(project_path)
    ctx.obj['api_key'] = api_key
    
    if not api_key:
        console.print("[yellow]Warning: No Gemini API key provided. Set GEMINI_API_KEY environment variable or use --api-key option.[/yellow]")


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force reindexing (clear existing data)')
@click.pass_context
def index(ctx, force):
    """Index the codebase for semantic search."""
    project_path = ctx.obj['project_path']
    api_key = ctx.obj['api_key']
    
    console.print(f"[blue]Indexing codebase at: {project_path}[/blue]")
    
    try:
        debugger = AIDebugger(project_path, api_key)
        
        with console.status("[bold green]Indexing codebase..."):
            result = debugger.index_codebase(force_reindex=force)
        
        if result['success']:
            console.print("[green]✓ Indexing completed successfully![/green]")
            
            # Display stats
            table = Table(title="Indexing Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Chunks", str(result['total_chunks']))
            table.add_row("Files Processed", str(result['files_processed']))
            table.add_row("Index Time", f"{result['index_time_seconds']} seconds")
            
            # Add chunk type breakdown
            for chunk_type, count in result['chunks_by_type'].items():
                table.add_row(f"{chunk_type.title()} Chunks", str(count))
            
            console.print(table)
        else:
            console.print(f"[red]✗ Indexing failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('error_message')
@click.option('--traceback', '-t', help='Error traceback (optional)')
@click.option('--max-context', '-m', default=5, help='Maximum context chunks to retrieve')
@click.pass_context
def diagnose(ctx, error_message, traceback, max_context):
    """Diagnose an error and get AI-powered fix suggestions."""
    project_path = ctx.obj['project_path']
    api_key = ctx.obj['api_key']
    
    if not api_key:
        console.print("[red]Error: Gemini API key is required for diagnosis. Set GEMINI_API_KEY or use --api-key.[/red]")
        return
    
    console.print(f"[blue]Diagnosing error: {error_message}[/blue]")
    
    try:
        debugger = AIDebugger(project_path, api_key)
        
        with console.status("[bold green]Analyzing error and generating fix..."):
            result = debugger.diagnose_error(error_message, traceback or "", max_context)
        
        if result['success']:
            console.print("[green]✓ Error diagnosis completed![/green]")
            
            # Display error info
            console.print(Panel(error_message, title="Error Message", border_style="red"))
            
            if traceback:
                console.print(Panel(traceback, title="Traceback", border_style="yellow"))
            
            # Display relevant code context
            console.print(f"\n[cyan]Found {result['relevant_code_chunks']} relevant code chunks:[/cyan]")
            
            for i, chunk in enumerate(result['code_context'][:3], 1):  # Show top 3
                metadata = chunk['metadata']
                console.print(f"\n[bold]Code Chunk {i}:[/bold]")
                console.print(f"File: {metadata['file_path']}")
                console.print(f"Type: {metadata['chunk_type']} - {metadata['name']}")
                console.print(f"Similarity: {chunk['similarity_score']:.3f}")
                
                # Show code preview
                syntax = Syntax(chunk['preview'], "python", theme="monokai", line_numbers=True)
                console.print(syntax)
            
            # Display AI fix suggestion
            console.print(Panel(
                Markdown(result['ai_fix_suggestion']), 
                title="AI Fix Suggestion", 
                border_style="green"
            ))
            
        else:
            console.print(f"[red]✗ Diagnosis failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('query')
@click.option('--max-results', '-m', default=10, help='Maximum number of results')
@click.pass_context
def search(ctx, query, max_results):
    """Search for code using natural language."""
    project_path = ctx.obj['project_path']
    api_key = ctx.obj['api_key']
    
    console.print(f"[blue]Searching for: {query}[/blue]")
    
    try:
        debugger = AIDebugger(project_path, api_key)
        
        with console.status("[bold green]Searching codebase..."):
            result = debugger.search_code(query, max_results)
        
        if result['success']:
            console.print(f"[green]✓ Found {result['results_count']} results![/green]")
            
            for i, chunk in enumerate(result['results'], 1):
                metadata = chunk['metadata']
                console.print(f"\n[bold]Result {i}:[/bold]")
                console.print(f"File: {metadata['file_path']}")
                console.print(f"Type: {metadata['chunk_type']} - {metadata['name']}")
                console.print(f"Relevance: {chunk['relevance_score']:.3f}")
                console.print(f"Lines: {metadata['start_line']}-{metadata['end_line']}")
                
                # Show code preview
                syntax = Syntax(chunk['preview'], "python", theme="monokai", line_numbers=True)
                console.print(syntax)
                
        else:
            console.print(f"[red]✗ Search failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--file-path', '-f', required=True, help='Path to the file')
@click.option('--function', help='Function name to explain')
@click.option('--class-name', help='Class name to explain')
@click.option('--question', '-q', help='Specific question about the code')
@click.pass_context
def explain(ctx, file_path, function, class_name, question):
    """Get an AI explanation of specific code."""
    project_path = ctx.obj['project_path']
    api_key = ctx.obj['api_key']
    
    if not api_key:
        console.print("[red]Error: Gemini API key is required for explanations. Set GEMINI_API_KEY or use --api-key.[/red]")
        return
    
    console.print(f"[blue]Explaining code in: {file_path}[/blue]")
    
    try:
        debugger = AIDebugger(project_path, api_key)
        
        with console.status("[bold green]Generating explanation..."):
            result = debugger.explain_code(file_path, function, class_name, question or "")
        
        if result['success']:
            console.print("[green]✓ Code explanation generated![/green]")
            
            # Display code
            syntax = Syntax(result['code_chunk'], "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Code: {file_path}", border_style="blue"))
            
            # Display explanation
            console.print(Panel(
                Markdown(result['explanation']), 
                title="AI Explanation", 
                border_style="green"
            ))
            
        else:
            console.print(f"[red]✗ Explanation failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--file-path', '-f', required=True, help='Path to the file')
@click.option('--function', help='Function name to improve')
@click.option('--class-name', help='Class name to improve')
@click.pass_context
def improve(ctx, file_path, function, class_name):
    """Get AI-powered improvement suggestions for code."""
    project_path = ctx.obj['project_path']
    api_key = ctx.obj['api_key']
    
    if not api_key:
        console.print("[red]Error: Gemini API key is required for improvements. Set GEMINI_API_KEY or use --api-key.[/red]")
        return
    
    console.print(f"[blue]Analyzing code for improvements: {file_path}[/blue]")
    
    try:
        debugger = AIDebugger(project_path, api_key)
        
        with console.status("[bold green]Generating improvement suggestions..."):
            result = debugger.suggest_improvements(file_path, function, class_name)
        
        if result['success']:
            console.print("[green]✓ Improvement suggestions generated![/green]")
            
            # Display original code
            syntax = Syntax(result['original_code'], "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Original Code", border_style="yellow"))
            
            # Display improvements
            console.print(Panel(
                Markdown(result['improvement_suggestions']), 
                title="AI Improvement Suggestions", 
                border_style="green"
            ))
            
        else:
            console.print(f"[red]✗ Improvement generation failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show statistics about the indexed codebase."""
    project_path = ctx.obj['project_path']
    api_key = ctx.obj['api_key']
    
    try:
        debugger = AIDebugger(project_path, api_key)
        stats_data = debugger.get_stats()
        
        table = Table(title="Codebase Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Project Path", stats_data['project_path'])
        table.add_row("Indexed", "Yes" if stats_data['is_indexed'] else "No")
        table.add_row("Total Chunks", str(stats_data['total_chunks']))
        table.add_row("Embedding Model", stats_data['embedding_model'])
        table.add_row("Embedding Dimension", str(stats_data['embedding_dimension']))
        
        if stats_data['last_index_time']:
            import datetime
            last_index = datetime.datetime.fromtimestamp(stats_data['last_index_time'])
            table.add_row("Last Indexed", last_index.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli()