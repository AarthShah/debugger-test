"""Code parser for extracting meaningful chunks from source code files."""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Generator
from dataclasses import dataclass

from config import SUPPORTED_EXTENSIONS, IGNORE_PATTERNS


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata."""
    content: str
    file_path: str
    chunk_type: str  # 'function', 'class', 'method', 'file'
    name: str
    start_line: int
    end_line: int
    docstring: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "content": self.content,
            "file_path": self.file_path,
            "chunk_type": self.chunk_type,
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "docstring": self.docstring
        }


class CodeParser:
    """Parser for extracting meaningful code chunks from source files."""
    
    def __init__(self):
        self.supported_extensions = SUPPORTED_EXTENSIONS
        self.ignore_patterns = IGNORE_PATTERNS
    
    def should_ignore_path(self, path: Path) -> bool:
        """Check if a path should be ignored based on ignore patterns."""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.ignore_patterns)
    
    def find_source_files(self, root_path: str) -> Generator[Path, None, None]:
        """Find all source code files in the given directory."""
        root = Path(root_path)
        
        for file_path in root.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix in self.supported_extensions and
                not self.should_ignore_path(file_path)):
                yield file_path
    
    def parse_python_file(self, file_path: Path) -> List[CodeChunk]:
        """Parse a Python file and extract functions, classes, and methods."""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Add the entire file as a chunk
            chunks.append(CodeChunk(
                content=content,
                file_path=str(file_path),
                chunk_type="file",
                name=file_path.name,
                start_line=1,
                end_line=len(lines),
                docstring=ast.get_docstring(tree) or ""
            ))
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunk = self._extract_function_chunk(node, lines, file_path)
                    if chunk:
                        chunks.append(chunk)
                
                elif isinstance(node, ast.ClassDef):
                    chunk = self._extract_class_chunk(node, lines, file_path)
                    if chunk:
                        chunks.append(chunk)
                        
                        # Extract methods within the class
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                method_chunk = self._extract_function_chunk(
                                    item, lines, file_path, parent_class=node.name
                                )
                                if method_chunk:
                                    chunks.append(method_chunk)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return chunks
    
    def _extract_function_chunk(self, node: ast.FunctionDef, lines: List[str], 
                               file_path: Path, parent_class: str = None) -> CodeChunk:
        """Extract a function or method chunk from AST node."""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        # Get the function content
        content = '\n'.join(lines[start_line-1:end_line])
        
        # Determine chunk type
        chunk_type = "method" if parent_class else "function"
        name = f"{parent_class}.{node.name}" if parent_class else node.name
        
        return CodeChunk(
            content=content,
            file_path=str(file_path),
            chunk_type=chunk_type,
            name=name,
            start_line=start_line,
            end_line=end_line,
            docstring=ast.get_docstring(node) or ""
        )
    
    def _extract_class_chunk(self, node: ast.ClassDef, lines: List[str], 
                           file_path: Path) -> CodeChunk:
        """Extract a class chunk from AST node."""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        # Get the class content
        content = '\n'.join(lines[start_line-1:end_line])
        
        return CodeChunk(
            content=content,
            file_path=str(file_path),
            chunk_type="class",
            name=node.name,
            start_line=start_line,
            end_line=end_line,
            docstring=ast.get_docstring(node) or ""
        )
    
    def parse_file(self, file_path: Path) -> List[CodeChunk]:
        """Parse a single file and return code chunks."""
        if file_path.suffix == ".py":
            return self.parse_python_file(file_path)
        else:
            # For non-Python files, treat the entire file as one chunk
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return [CodeChunk(
                    content=content,
                    file_path=str(file_path),
                    chunk_type="file",
                    name=file_path.name,
                    start_line=1,
                    end_line=len(content.split('\n')),
                    docstring=""
                )]
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return []
    
    def parse_codebase(self, root_path: str) -> List[CodeChunk]:
        """Parse an entire codebase and return all code chunks."""
        all_chunks = []
        
        for file_path in self.find_source_files(root_path):
            chunks = self.parse_file(file_path)
            all_chunks.extend(chunks)
        
        return all_chunks