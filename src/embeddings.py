"""Vector embeddings generation for code chunks using sentence-transformers."""

import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL
from .code_parser import CodeChunk


class EmbeddingGenerator:
    """Generates vector embeddings for code chunks."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding model."""
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            raise
    
    def prepare_text_for_embedding(self, chunk: CodeChunk) -> str:
        """Prepare code chunk text for embedding generation."""
        # Combine different parts of the code chunk for better context
        parts = []
        
        # Add file path context
        parts.append(f"File: {chunk.file_path}")
        
        # Add chunk type and name
        parts.append(f"{chunk.chunk_type.title()}: {chunk.name}")
        
        # Add docstring if available
        if chunk.docstring:
            parts.append(f"Documentation: {chunk.docstring}")
        
        # Add the actual code content
        parts.append(f"Code:\n{chunk.content}")
        
        return "\n\n".join(parts)
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def generate_chunk_embedding(self, chunk: CodeChunk) -> np.ndarray:
        """Generate embedding for a code chunk."""
        text = self.prepare_text_for_embedding(chunk)
        return self.generate_embedding(text)
    
    def generate_embeddings_batch(self, chunks: List[CodeChunk]) -> List[np.ndarray]:
        """Generate embeddings for multiple code chunks efficiently."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        texts = [self.prepare_text_for_embedding(chunk) for chunk in chunks]
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            return embeddings
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return self.model.get_sentence_embedding_dimension()