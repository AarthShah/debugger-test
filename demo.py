"""Simple demo of the AI debugger without heavy dependencies."""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.code_parser import CodeParser


def main():
    """Demonstrate the core parsing functionality."""
    print("🚀 AI-Powered Debugger - Core Demo")
    print("=" * 50)
    
    # Initialize parser
    parser = CodeParser()
    
    # Parse current directory
    print(f"\n📁 Parsing codebase in: {Path.cwd()}")
    
    try:
        chunks = parser.parse_codebase(".")
        
        if not chunks:
            print("❌ No code chunks found")
            return
            
        print(f"✅ Found {len(chunks)} code chunks!")
        
        # Show statistics
        chunk_types = {}
        files = set()
        
        for chunk in chunks:
            chunk_types[chunk.chunk_type] = chunk_types.get(chunk.chunk_type, 0) + 1
            files.add(chunk.file_path)
        
        print(f"\n📊 Statistics:")
        print(f"   Files processed: {len(files)}")
        print(f"   Total chunks: {len(chunks)}")
        
        print(f"\n📋 Chunk breakdown:")
        for chunk_type, count in chunk_types.items():
            print(f"   {chunk_type}: {count}")
        
        # Show some examples
        print(f"\n💻 Sample code chunks:")
        for i, chunk in enumerate(chunks[:5], 1):
            print(f"\n{i}. {chunk.chunk_type.title()}: {chunk.name}")
            print(f"   📄 File: {chunk.file_path}")
            print(f"   📍 Lines: {chunk.start_line}-{chunk.end_line}")
            if chunk.docstring:
                print(f"   📝 Doc: {chunk.docstring[:80]}...")
            
            # Show a few lines of code
            lines = chunk.content.split('\n')
            preview = '\n'.join(lines[:3])
            if len(lines) > 3:
                preview += '\n   ...'
            print(f"   Code preview:")
            for line in preview.split('\n'):
                print(f"     {line}")
        
        print(f"\n🔍 Semantic Search Ready:")
        print("   With full dependencies installed, you can:")
        print("   • Generate vector embeddings for all chunks")
        print("   • Store in ChromaDB for fast similarity search")
        print("   • Use Gemini API for AI-powered bug fixes")
        print("   • Search using natural language queries")
        
        print(f"\n📚 Next Steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Set GEMINI_API_KEY environment variable")
        print("   3. Run: python main.py index")
        print("   4. Run: python main.py diagnose 'your error message'")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")


if __name__ == "__main__":
    main()