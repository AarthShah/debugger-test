"""Example usage of the AI-powered debugger."""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.debugger import AIDebugger


def main():
    """Demonstrate the AI debugger functionality."""
    print("AI-Powered Debugger Example")
    print("=" * 40)
    
    # Initialize debugger with current directory
    project_path = "."
    debugger = AIDebugger(project_path)
    
    try:
        # Index the codebase
        print("\n1. Indexing codebase...")
        result = debugger.index_codebase()
        
        if result['success']:
            print(f"✓ Indexed {result['total_chunks']} code chunks")
            print(f"  - Files processed: {result['files_processed']}")
            print(f"  - Index time: {result['index_time_seconds']} seconds")
            
            # Show chunk breakdown
            print("\nChunk breakdown:")
            for chunk_type, count in result['chunks_by_type'].items():
                print(f"  - {chunk_type}: {count}")
        else:
            print(f"✗ Indexing failed: {result.get('error')}")
            return
        
        # Example search
        print("\n2. Searching for code...")
        search_result = debugger.search_code("function that parses code", max_results=3)
        
        if search_result['success']:
            print(f"✓ Found {search_result['results_count']} relevant code chunks")
            
            for i, chunk in enumerate(search_result['results'][:2], 1):
                metadata = chunk['metadata']
                print(f"\nResult {i}:")
                print(f"  File: {metadata['file_path']}")
                print(f"  Type: {metadata['chunk_type']} - {metadata['name']}")
                print(f"  Relevance: {chunk['relevance_score']:.3f}")
        else:
            print(f"✗ Search failed: {search_result.get('error')}")
        
        # Example error diagnosis (without API key, will show what would happen)
        print("\n3. Example error diagnosis...")
        print("Note: This would require a Gemini API key for full functionality")
        
        error_msg = "AttributeError: 'NoneType' object has no attribute 'parse'"
        traceback = """
Traceback (most recent call last):
  File "src/code_parser.py", line 45, in parse_file
    tree = ast.parse(content)
  File "src/code_parser.py", line 50, in _extract_function_chunk
    content.parse()
AttributeError: 'NoneType' object has no attribute 'parse'
"""
        
        print(f"Error: {error_msg}")
        print("\nWith a Gemini API key, the system would:")
        print("1. Find relevant code chunks related to the error")
        print("2. Analyze the context and error details")
        print("3. Generate AI-powered fix suggestions")
        print("4. Provide explanations and improvements")
        
        # Show stats
        print("\n4. Debugger statistics...")
        stats = debugger.get_stats()
        print(f"✓ Total chunks indexed: {stats['total_chunks']}")
        print(f"  - Embedding model: {stats['embedding_model']}")
        print(f"  - Embedding dimension: {stats['embedding_dimension']}")
        print(f"  - Project path: {stats['project_path']}")
        
    except Exception as e:
        print(f"Error during example: {e}")


if __name__ == "__main__":
    main()