"""Tests for the code parser module."""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.code_parser import CodeParser, CodeChunk


class TestCodeParser(unittest.TestCase):
    """Test cases for CodeParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
        self.temp_dir = tempfile.mkdtemp()
    
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
    
    def test_parse_python_function(self):
        """Test parsing a simple Python function."""
        content = '''def hello_world():
    """A simple greeting function."""
    print("Hello, world!")
    return "Hello"
'''
        file_path = self.create_test_file("test.py", content)
        chunks = self.parser.parse_python_file(file_path)
        
        # Should have file chunk and function chunk
        self.assertEqual(len(chunks), 2)
        
        # Check function chunk
        function_chunk = next(c for c in chunks if c.chunk_type == "function")
        self.assertEqual(function_chunk.name, "hello_world")
        self.assertEqual(function_chunk.docstring, "A simple greeting function.")
        self.assertEqual(function_chunk.start_line, 1)
    
    def test_parse_python_class(self):
        """Test parsing a Python class with methods."""
        content = '''class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, x):
        """Add a number."""
        self.result += x
        return self.result
'''
        file_path = self.create_test_file("calculator.py", content)
        chunks = self.parser.parse_python_file(file_path)
        
        # Should have file, class, and method chunks
        chunk_types = [c.chunk_type for c in chunks]
        self.assertIn("file", chunk_types)
        self.assertIn("class", chunk_types)
        self.assertIn("method", chunk_types)
        
        # Check class chunk
        class_chunk = next(c for c in chunks if c.chunk_type == "class")
        self.assertEqual(class_chunk.name, "Calculator")
        self.assertEqual(class_chunk.docstring, "A simple calculator class.")
    
    def test_find_source_files(self):
        """Test finding source files in directory."""
        # Create test files
        self.create_test_file("test.py", "print('hello')")
        self.create_test_file("script.js", "console.log('hello');")
        self.create_test_file("readme.txt", "This is a readme")
        
        # Create ignored directory
        ignored_dir = Path(self.temp_dir) / "__pycache__"
        ignored_dir.mkdir()
        self.create_test_file("__pycache__/cached.py", "cached")
        
        files = list(self.parser.find_source_files(self.temp_dir))
        file_names = [f.name for f in files]
        
        self.assertIn("test.py", file_names)
        self.assertIn("script.js", file_names)
        self.assertNotIn("readme.txt", file_names)  # Not supported extension
        self.assertNotIn("cached.py", file_names)   # In ignored directory
    
    def test_should_ignore_path(self):
        """Test path ignoring logic."""
        test_cases = [
            ("/path/to/__pycache__/file.py", True),
            ("/path/to/node_modules/lib.js", True),
            ("/path/to/.git/config", True),
            ("/path/to/src/main.py", False),
            ("/normal/path/file.py", False)
        ]
        
        for path, should_ignore in test_cases:
            with self.subTest(path=path):
                result = self.parser.should_ignore_path(Path(path))
                self.assertEqual(result, should_ignore)


if __name__ == '__main__':
    unittest.main()