"""Vector database operations using ChromaDB for storing and searching code embeddings."""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings

from config import VECTOR_DB_PATH
from .code_parser import CodeChunk


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self, collection_name: str = "code_chunks"):
        """Initialize the vector store."""
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._setup_client()
    
    def _setup_client(self):
        """Set up ChromaDB client and collection."""
        try:
            # Ensure vector database directory exists
            os.makedirs(VECTOR_DB_PATH, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(VECTOR_DB_PATH),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Code chunks for semantic search"}
            )
            
            print(f"Vector store initialized with collection: {self.collection_name}")
            
        except Exception as e:
            print(f"Error setting up vector store: {e}")
            raise
    
    def add_chunks(self, chunks: List[CodeChunk], embeddings: List[List[float]]):
        """Add code chunks with their embeddings to the vector store."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        try:
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # Create unique ID for each chunk
                chunk_id = f"{chunk.file_path}:{chunk.chunk_type}:{chunk.name}:{chunk.start_line}"
                ids.append(chunk_id)
                
                # Document is the actual code content
                documents.append(chunk.content)
                
                # Metadata contains all other information
                metadata = {
                    "file_path": chunk.file_path,
                    "chunk_type": chunk.chunk_type,
                    "name": chunk.name,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "docstring": chunk.docstring
                }
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            print(f"Error adding chunks to vector store: {e}")
            raise
    
    def search_similar(self, query_embedding: List[float], 
                      n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar code chunks using vector similarity."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    result = {
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity_score": 1 - results["distances"][0][i]  # Convert distance to similarity
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching vector store: {e}")
            raise
    
    def search_by_metadata(self, where_clause: Dict[str, Any], 
                          n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for chunks based on metadata filters."""
        try:
            results = self.collection.get(
                where=where_clause,
                limit=n_results,
                include=["documents", "metadatas"]
            )
            
            # Format results
            formatted_results = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    result = {
                        "id": results["ids"][i],
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i],
                        "similarity_score": 1.0  # Exact match
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching by metadata: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection_name
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"total_chunks": 0, "collection_name": self.collection_name}
    
    def clear_collection(self):
        """Clear all data from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Code chunks for semantic search"}
            )
            print(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            print(f"Error clearing collection: {e}")
            raise
    
    def update_chunk(self, chunk_id: str, chunk: CodeChunk, embedding: List[float]):
        """Update an existing chunk in the vector store."""
        try:
            # ChromaDB doesn't have direct update, so we upsert
            self.collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk.content],
                metadatas=[{
                    "file_path": chunk.file_path,
                    "chunk_type": chunk.chunk_type,
                    "name": chunk.name,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "docstring": chunk.docstring
                }]
            )
            print(f"Updated chunk: {chunk_id}")
        except Exception as e:
            print(f"Error updating chunk: {e}")
            raise
    
    def delete_chunks_by_file(self, file_path: str):
        """Delete all chunks from a specific file."""
        try:
            # Find all chunks from the file
            results = self.collection.get(
                where={"file_path": file_path},
                include=["documents", "metadatas"]
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"Deleted {len(results['ids'])} chunks from {file_path}")
        except Exception as e:
            print(f"Error deleting chunks from file {file_path}: {e}")
            raise