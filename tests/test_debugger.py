"""Tests for the debugger integration."""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from debugger import AIDebugger


class TestAIDebugger(unittest.TestCase):
    """Test cases for AIDebugger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a simple test codebase
        self.create_test_file("main.py", '''
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

def divide_numbers(x, y):
    """Divide two numbers."""
    return x / y  # Potential division by zero

class MathUtils:
    """Utility class for math operations."""
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
''')
        
        self.create_test_file("utils.py", '''
def parse_number(value):
    """Parse a string to number."""
    try:
        return int(value)
    except ValueError:
        return float(value)
''')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    
    def test_debugger_initialization(self):
        """Test debugger initialization."""
        debugger = AIDebugger(self.temp_dir)
        self.assertEqual(str(debugger.project_path), self.temp_dir)
        self.assertFalse(debugger.is_indexed)
    
    def test_index_codebase(self):
        """Test codebase indexing."""
        debugger = AIDebugger(self.temp_dir)
        
        # Mock the embedding generation to avoid requiring the actual model
        class MockEmbeddingGenerator:
            def __init__(self):
                self.model_name = "mock-model"
            
            def generate_embeddings_batch(self, chunks):
                import numpy as np
                # Return mock embeddings
                return np.random.rand(len(chunks), 384)
            
            def get_embedding_dimension(self):
                return 384
        
        # Mock vector store to avoid requiring ChromaDB
        class MockVectorStore:
            def __init__(self):
                self.chunks = []
                
            def add_chunks(self, chunks, embeddings):
                self.chunks.extend(chunks)
            
            def get_collection_stats(self):
                return {"total_chunks": len(self.chunks)}
            
            def clear_collection(self):
                self.chunks = []
        
        # Replace with mocks for testing
        debugger.embedding_generator = MockEmbeddingGenerator()
        debugger.vector_store = MockVectorStore()
        
        result = debugger.index_codebase()
        
        self.assertTrue(result['success'])
        self.assertGreater(result['total_chunks'], 0)
        self.assertTrue(debugger.is_indexed)
    
    def test_get_stats(self):
        """Test getting debugger statistics."""
        debugger = AIDebugger(self.temp_dir)
        stats = debugger.get_stats()
        
        self.assertIn('is_indexed', stats)
        self.assertIn('project_path', stats)
        self.assertEqual(stats['project_path'], self.temp_dir)


if __name__ == '__main__':
    unittest.main()