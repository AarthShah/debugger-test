# AI-Powered Debugger

An intelligent debugging system that uses semantic search and AI to help diagnose and fix bugs in your codebase.

## Features

🔍 **Semantic Code Analysis**: Parse your entire codebase into meaningful chunks (functions, classes, methods)  
🧠 **Vector Embeddings**: Store code as vector embeddings for intelligent semantic search  
🎯 **Smart Bug Diagnosis**: Find relevant code context when errors occur using similarity search  
🤖 **AI-Powered Fixes**: Use Google's Gemini API to generate accurate bug fixes and improvements  
📊 **Rich CLI Interface**: Beautiful command-line interface with syntax highlighting and progress bars  

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AarthShah/debugger-test.git
   cd debugger-test
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Gemini API key:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # Get your API key from: https://makersuite.google.com/app/apikey
   echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
   ```

## Quick Start

### 1. Index Your Codebase
```bash
python main.py index --project-path /path/to/your/project
```

### 2. Diagnose an Error
```bash
python main.py diagnose "AttributeError: 'NoneType' object has no attribute 'method'"
```

### 3. Search for Code
```bash
python main.py search "function that handles user authentication"
```

### 4. Get Code Explanations
```bash
python main.py explain --file-path src/main.py --function main_function
```

### 5. Get Improvement Suggestions
```bash
python main.py improve --file-path src/utils.py --function helper_function
```

## Core Components

### 🧩 Code Parser (`src/code_parser.py`)
- Extracts meaningful chunks from source code files
- Supports Python (with AST parsing) and other languages
- Identifies functions, classes, methods, and file-level code
- Filters out irrelevant files and directories

### 🔢 Embedding Generator (`src/embeddings.py`)
- Uses sentence-transformers to generate vector embeddings
- Combines code content with metadata for better context
- Supports batch processing for efficiency
- Default model: `all-MiniLM-L6-v2` (384 dimensions)

### 🗄️ Vector Store (`src/vector_store.py`)
- ChromaDB-based vector database for storing embeddings
- Supports similarity search and metadata filtering
- Persistent storage with automatic collection management
- Efficient batch operations and updates

### 🔍 Semantic Search (`src/semantic_search.py`)
- Advanced semantic search capabilities
- Error-aware search with traceback analysis
- Relevance scoring and result ranking
- Context-aware result enhancement

### 🤖 Gemini Client (`src/gemini_client.py`)
- Integration with Google's Gemini API
- Specialized prompts for bug fixing, code improvement, and explanation
- Structured response formatting
- Error handling and retry logic

### 🎛️ Main Orchestrator (`src/debugger.py`)
- Coordinates all components
- Provides high-level API for common operations
- Manages indexing and search workflows
- Statistics and monitoring

## Usage Examples

### Programmatic API

```python
from src.debugger import AIDebugger

# Initialize debugger
debugger = AIDebugger("/path/to/your/project", gemini_api_key="your_key")

# Index the codebase
result = debugger.index_codebase()
print(f"Indexed {result['total_chunks']} code chunks")

# Diagnose an error
error_result = debugger.diagnose_error(
    error_message="NameError: name 'undefined_var' is not defined",
    error_traceback="...",  # Full traceback
    max_context_chunks=5
)

if error_result['success']:
    print("AI Fix Suggestion:")
    print(error_result['ai_fix_suggestion'])

# Search for specific code
search_result = debugger.search_code("database connection logic")
for chunk in search_result['results']:
    print(f"Found: {chunk['metadata']['name']} in {chunk['metadata']['file_path']}")
```

### Command Line Interface

```bash
# Show help
python main.py --help

# Index with force refresh
python main.py index --force

# Diagnose with traceback file
python main.py diagnose "ValueError: invalid literal" --traceback "$(cat traceback.txt)"

# Search with custom result limit
python main.py search "error handling" --max-results 15

# Explain specific class method
python main.py explain --file-path src/models.py --class-name User --function get_profile

# View statistics
python main.py stats
```

## Configuration

Edit `config.py` to customize:

```python
# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # or "all-mpnet-base-v2" for better quality
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Search settings
MAX_SEARCH_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3

# File filtering
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp", ".c"}
IGNORE_PATTERNS = {"__pycache__", "node_modules", ".git", "venv"}
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Parser   │───▶│  Embedding Gen  │───▶│  Vector Store   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Semantic Search │◀───┤ AI Debugger     │───▶│ Gemini Client   │
└─────────────────┘    │ (Orchestrator)  │    └─────────────────┘
                       └─────────────────┘
                               │
                               ▼
                       ┌─────────────────┐
                       │   CLI/API       │
                       └─────────────────┘
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_code_parser.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

Run the example:

```bash
python example.py
```

## Supported Languages

Currently optimized for:
- **Python** (full AST parsing with functions, classes, methods)
- **JavaScript/TypeScript** (file-level parsing)
- **Java** (file-level parsing)
- **C/C++** (file-level parsing)

## Performance Notes

- **Indexing**: ~100-500 chunks per second depending on hardware
- **Search**: Sub-second semantic search on thousands of chunks
- **Memory**: ~1MB per 1000 code chunks stored
- **API Calls**: One Gemini API call per diagnosis/explanation request

## Limitations

- Requires Gemini API key for AI-powered features
- Large codebases (>10k files) may require significant indexing time
- Non-English code comments may affect embedding quality
- API rate limits apply for Gemini requests

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure tests pass: `python -m pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Roadmap

- [ ] Support for more programming languages with AST parsing
- [ ] Web interface for easier visualization
- [ ] Integration with popular IDEs (VS Code, PyCharm)
- [ ] Continuous monitoring and automatic error detection
- [ ] Team collaboration features
- [ ] Custom model fine-tuning for specific codebases