"""Main AI-powered debugger that orchestrates all components."""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from .code_parser import CodeParser, CodeChunk
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
from .semantic_search import SemanticSearcher
from .gemini_client import GeminiClient


class AIDebugger:
    """Main AI-powered debugger class that coordinates all components."""
    
    def __init__(self, project_path: str, gemini_api_key: str = None):
        """Initialize the AI debugger with a project path."""
        self.project_path = Path(project_path)
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        # Initialize components
        self.code_parser = CodeParser()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.semantic_searcher = SemanticSearcher(self.embedding_generator, self.vector_store)
        self.gemini_client = GeminiClient(gemini_api_key)
        
        # Track indexing status
        self.is_indexed = False
        self.last_index_time = None
    
    def index_codebase(self, force_reindex: bool = False) -> Dict[str, Any]:
        """Parse and index the entire codebase into the vector database."""
        print(f"Starting to index codebase at: {self.project_path}")
        start_time = time.time()
        
        try:
            # Clear existing data if force reindexing
            if force_reindex:
                print("Force reindexing: clearing existing data...")
                self.vector_store.clear_collection()
            
            # Parse codebase
            print("Parsing codebase...")
            chunks = self.code_parser.parse_codebase(str(self.project_path))
            
            if not chunks:
                print("No code chunks found to index.")
                return {"success": False, "message": "No code chunks found"}
            
            print(f"Found {len(chunks)} code chunks")
            
            # Generate embeddings
            print("Generating embeddings...")
            embeddings = self.embedding_generator.generate_embeddings_batch(chunks)
            
            # Store in vector database
            print("Storing in vector database...")
            self.vector_store.add_chunks(chunks, embeddings.tolist())
            
            # Update status
            self.is_indexed = True
            self.last_index_time = time.time()
            
            end_time = time.time()
            index_time = end_time - start_time
            
            result = {
                "success": True,
                "total_chunks": len(chunks),
                "index_time_seconds": round(index_time, 2),
                "chunks_by_type": self._get_chunks_by_type(chunks),
                "files_processed": len(set(chunk.file_path for chunk in chunks))
            }
            
            print(f"Indexing completed in {index_time:.2f} seconds")
            print(f"Processed {result['files_processed']} files, {result['total_chunks']} chunks")
            
            return result
            
        except Exception as e:
            print(f"Error during indexing: {e}")
            return {"success": False, "error": str(e)}
    
    def diagnose_error(self, error_message: str, error_traceback: str = "", 
                      max_context_chunks: int = 5) -> Dict[str, Any]:
        """Diagnose an error and provide AI-powered fix suggestions."""
        if not self.is_indexed:
            return {
                "success": False, 
                "error": "Codebase not indexed. Please run index_codebase() first."
            }
        
        print(f"Diagnosing error: {error_message}")
        
        try:
            # Search for relevant code context
            print("Searching for relevant code context...")
            relevant_chunks = self.semantic_searcher.search_for_error(
                error_message, error_traceback, max_context_chunks
            )
            
            if not relevant_chunks:
                return {
                    "success": False,
                    "error": "No relevant code context found for this error."
                }
            
            print(f"Found {len(relevant_chunks)} relevant code chunks")
            
            # Generate AI-powered fix
            print("Generating AI-powered fix suggestion...")
            fix_suggestion = self.gemini_client.generate_bug_fix(
                error_message, error_traceback, relevant_chunks
            )
            
            result = {
                "success": True,
                "error_message": error_message,
                "error_traceback": error_traceback,
                "relevant_code_chunks": len(relevant_chunks),
                "code_context": relevant_chunks,
                "ai_fix_suggestion": fix_suggestion,
                "timestamp": time.time()
            }
            
            print("Error diagnosis completed")
            return result
            
        except Exception as e:
            print(f"Error during diagnosis: {e}")
            return {"success": False, "error": str(e)}
    
    def search_code(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search for code chunks based on a natural language query."""
        if not self.is_indexed:
            return {
                "success": False,
                "error": "Codebase not indexed. Please run index_codebase() first."
            }
        
        print(f"Searching for: {query}")
        
        try:
            results = self.semantic_searcher.search(query, max_results)
            
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error during search: {e}")
            return {"success": False, "error": str(e)}
    
    def explain_code(self, file_path: str, function_name: str = None, 
                    class_name: str = None, specific_question: str = "") -> Dict[str, Any]:
        """Get an AI explanation of specific code."""
        if not self.is_indexed:
            return {
                "success": False,
                "error": "Codebase not indexed. Please run index_codebase() first."
            }
        
        try:
            # Build search query
            query_parts = [f"file:{file_path}"]
            if function_name:
                query_parts.append(f"function:{function_name}")
            if class_name:
                query_parts.append(f"class:{class_name}")
            
            query = " ".join(query_parts)
            search_results = self.semantic_searcher.search(query, max_results=1)
            
            if not search_results:
                return {
                    "success": False,
                    "error": f"No code found matching: {query}"
                }
            
            # Get the most relevant chunk
            code_chunk = search_results[0]["content"]
            
            # Generate explanation
            explanation = self.gemini_client.explain_code(code_chunk, specific_question)
            
            return {
                "success": True,
                "file_path": file_path,
                "function_name": function_name,
                "class_name": class_name,
                "code_chunk": code_chunk,
                "explanation": explanation,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error explaining code: {e}")
            return {"success": False, "error": str(e)}
    
    def suggest_improvements(self, file_path: str, function_name: str = None, 
                           class_name: str = None) -> Dict[str, Any]:
        """Get AI-powered improvement suggestions for specific code."""
        if not self.is_indexed:
            return {
                "success": False,
                "error": "Codebase not indexed. Please run index_codebase() first."
            }
        
        try:
            # Build search query
            query_parts = [f"file:{file_path}"]
            if function_name:
                query_parts.append(f"function:{function_name}")
            if class_name:
                query_parts.append(f"class:{class_name}")
            
            query = " ".join(query_parts)
            search_results = self.semantic_searcher.search(query, max_results=1)
            
            if not search_results:
                return {
                    "success": False,
                    "error": f"No code found matching: {query}"
                }
            
            # Get the most relevant chunk
            code_chunk = search_results[0]["content"]
            metadata = search_results[0]["metadata"]
            
            # Generate improvement suggestions
            context = f"This is a {metadata['chunk_type']} named {metadata['name']} from {metadata['file_path']}"
            improvements = self.gemini_client.suggest_code_improvement(code_chunk, context)
            
            return {
                "success": True,
                "file_path": file_path,
                "function_name": function_name,
                "class_name": class_name,
                "original_code": code_chunk,
                "improvement_suggestions": improvements,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error generating improvements: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed codebase."""
        stats = self.vector_store.get_collection_stats()
        
        stats.update({
            "is_indexed": self.is_indexed,
            "last_index_time": self.last_index_time,
            "project_path": str(self.project_path),
            "embedding_model": self.embedding_generator.model_name,
            "embedding_dimension": self.embedding_generator.get_embedding_dimension()
        })
        
        return stats
    
    def _get_chunks_by_type(self, chunks: List[CodeChunk]) -> Dict[str, int]:
        """Get count of chunks by type."""
        chunk_counts = {}
        for chunk in chunks:
            chunk_type = chunk.chunk_type
            chunk_counts[chunk_type] = chunk_counts.get(chunk_type, 0) + 1
        return chunk_counts
    
    def update_file(self, file_path: str) -> Dict[str, Any]:
        """Update the index for a specific file (useful for incremental updates)."""
        if not self.is_indexed:
            return {
                "success": False,
                "error": "Codebase not indexed. Please run index_codebase() first."
            }
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {"success": False, "error": f"File does not exist: {file_path}"}
            
            # Delete existing chunks for this file
            self.vector_store.delete_chunks_by_file(str(file_path_obj))
            
            # Parse and index the updated file
            chunks = self.code_parser.parse_file(file_path_obj)
            
            if chunks:
                embeddings = self.embedding_generator.generate_embeddings_batch(chunks)
                self.vector_store.add_chunks(chunks, embeddings.tolist())
            
            return {
                "success": True,
                "file_path": file_path,
                "chunks_updated": len(chunks),
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error updating file {file_path}: {e}")
            return {"success": False, "error": str(e)}