"""Semantic search functionality for finding relevant code chunks based on errors or queries."""

from typing import List, Dict, Any, Optional
import re

from config import MAX_SEARCH_RESULTS, SIMILARITY_THRESHOLD
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore


class SemanticSearcher:
    """Performs semantic search on code chunks to find relevant context."""
    
    def __init__(self, embedding_generator: EmbeddingGenerator, vector_store: VectorStore):
        """Initialize with embedding generator and vector store."""
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
    
    def search_for_error(self, error_message: str, error_traceback: str = "", 
                        max_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """Search for code chunks relevant to an error message and traceback."""
        # Combine error message and traceback for better context
        query_parts = []
        
        if error_message:
            query_parts.append(f"Error: {error_message}")
        
        if error_traceback:
            # Extract relevant parts from traceback
            traceback_info = self._extract_traceback_info(error_traceback)
            if traceback_info:
                query_parts.append(f"Traceback context: {traceback_info}")
        
        query_text = "\n".join(query_parts)
        
        return self.search(query_text, max_results)
    
    def search_for_function(self, function_name: str, context: str = "", 
                           max_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """Search for code chunks related to a specific function."""
        query_parts = [f"Function: {function_name}"]
        
        if context:
            query_parts.append(f"Context: {context}")
        
        query_text = "\n".join(query_parts)
        
        return self.search(query_text, max_results)
    
    def search_for_class(self, class_name: str, context: str = "", 
                        max_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """Search for code chunks related to a specific class."""
        query_parts = [f"Class: {class_name}"]
        
        if context:
            query_parts.append(f"Context: {context}")
        
        query_text = "\n".join(query_parts)
        
        return self.search(query_text, max_results)
    
    def search(self, query_text: str, max_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """Perform semantic search for a general query."""
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_generator.generate_embedding(query_text)
            
            # Search in vector store
            results = self.vector_store.search_similar(
                query_embedding.tolist(), 
                n_results=max_results
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in results 
                if result["similarity_score"] >= SIMILARITY_THRESHOLD
            ]
            
            # Enhance results with additional context
            enhanced_results = self._enhance_search_results(filtered_results, query_text)
            
            return enhanced_results
            
        except Exception as e:
            print(f"Error during semantic search: {e}")
            return []
    
    def _extract_traceback_info(self, traceback: str) -> str:
        """Extract relevant information from error traceback."""
        if not traceback:
            return ""
        
        # Extract file names, function names, and line numbers
        info_parts = []
        
        # Look for file paths and line numbers
        file_pattern = r'File "([^"]+)", line (\d+)'
        file_matches = re.findall(file_pattern, traceback)
        
        for file_path, line_num in file_matches:
            info_parts.append(f"File: {file_path} line {line_num}")
        
        # Look for function names
        function_pattern = r'in (\w+)'
        function_matches = re.findall(function_pattern, traceback)
        
        for func_name in function_matches:
            info_parts.append(f"Function: {func_name}")
        
        # Look for class names (assuming they start with capital letters)
        class_pattern = r'(\b[A-Z]\w*)\.'
        class_matches = re.findall(class_pattern, traceback)
        
        for class_name in class_matches:
            info_parts.append(f"Class: {class_name}")
        
        return " ".join(set(info_parts))  # Remove duplicates
    
    def _enhance_search_results(self, results: List[Dict[str, Any]], 
                               query_text: str) -> List[Dict[str, Any]]:
        """Enhance search results with additional context and ranking."""
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # Add relevance score based on multiple factors
            relevance_score = self._calculate_relevance_score(result, query_text)
            enhanced_result["relevance_score"] = relevance_score
            
            # Add snippet preview
            enhanced_result["preview"] = self._generate_code_preview(result["content"])
            
            # Add file context
            enhanced_result["file_context"] = self._get_file_context(result["metadata"])
            
            enhanced_results.append(enhanced_result)
        
        # Sort by relevance score (descending)
        enhanced_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return enhanced_results
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query_text: str) -> float:
        """Calculate a relevance score for a search result."""
        score = result["similarity_score"]
        
        # Boost score for function/method chunks if query mentions functions
        if "function" in query_text.lower() and result["metadata"]["chunk_type"] in ["function", "method"]:
            score += 0.1
        
        # Boost score for class chunks if query mentions classes
        if "class" in query_text.lower() and result["metadata"]["chunk_type"] == "class":
            score += 0.1
        
        # Boost score if chunk has documentation
        if result["metadata"]["docstring"]:
            score += 0.05
        
        # Cap the score at 1.0
        return min(score, 1.0)
    
    def _generate_code_preview(self, code_content: str, max_lines: int = 10) -> str:
        """Generate a preview of the code content."""
        lines = code_content.split('\n')
        
        if len(lines) <= max_lines:
            return code_content
        
        # Take first few lines and add ellipsis
        preview_lines = lines[:max_lines]
        preview_lines.append("...")
        
        return '\n'.join(preview_lines)
    
    def _get_file_context(self, metadata: Dict[str, Any]) -> str:
        """Generate file context information."""
        context_parts = []
        
        context_parts.append(f"File: {metadata['file_path']}")
        context_parts.append(f"Type: {metadata['chunk_type']}")
        context_parts.append(f"Name: {metadata['name']}")
        context_parts.append(f"Lines: {metadata['start_line']}-{metadata['end_line']}")
        
        return " | ".join(context_parts)
    
    def search_by_file_type(self, file_extension: str, query_text: str = "", 
                           max_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
        """Search for chunks from files with specific extension."""
        # Use metadata search for file type filtering
        where_clause = {"file_path": {"$contains": file_extension}}
        
        results = self.vector_store.search_by_metadata(where_clause, max_results)
        
        # If there's a query, also do semantic search and combine results
        if query_text:
            semantic_results = self.search(query_text, max_results)
            # Filter semantic results by file type and combine
            filtered_semantic = [
                r for r in semantic_results 
                if file_extension in r["metadata"]["file_path"]
            ]
            
            # Combine and deduplicate results
            combined_results = {}
            for result in results + filtered_semantic:
                combined_results[result["id"]] = result
            
            return list(combined_results.values())
        
        return results