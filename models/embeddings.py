import os
import json
from typing import Tuple, List, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from database_dummy import db
import config

class EmbeddingManager:
    """Manages embeddings and FAISS indices"""
    
    def __init__(self):
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        os.makedirs(config.FAISS_INDEX_DIR, exist_ok=True)
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        return self.model.encode(texts, convert_to_numpy=True)
    
    def save_embedding_to_db(self, chunk_id: int, embedding: np.ndarray):
        """Save embedding vector to database"""
        db.insert_embedding(chunk_id, embedding)
    
    def load_embeddings_from_db(self, pdf_id: int = None) -> Tuple[np.ndarray, List[int]]:
        """
        Load embeddings from database
        Returns: (embeddings_array, chunk_ids_list)
        """
        results = db.get_embeddings_by_pdf(pdf_id)
        
        embeddings = []
        chunk_ids = []
        
        for embedding_id, chunk_id, vector in results:
            # Vector is already a numpy array from dummy DB
            if isinstance(vector, list):
                vector = np.array(vector)
            embeddings.append(vector)
            chunk_ids.append(chunk_id)
        
        if embeddings:
            return np.array(embeddings), chunk_ids
        return np.array([]), []
    
    def create_faiss_index(self, pdf_id: int = None) -> Tuple[Optional[faiss.Index], List[int]]:
        """Create or update FAISS index from database embeddings"""
        embeddings, chunk_ids = self.load_embeddings_from_db(pdf_id)
        
        if len(embeddings) == 0:
            return None, []
        
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(embeddings.astype('float32'))
        
        return index, chunk_ids
    
    def save_faiss_index(self, index: faiss.Index, chunk_ids: List[int], pdf_id: int = None):
        """Save FAISS index to disk"""
        if pdf_id:
            index_path = os.path.join(config.FAISS_INDEX_DIR, f"index_{pdf_id}.faiss")
            ids_path = os.path.join(config.FAISS_INDEX_DIR, f"ids_{pdf_id}.json")
        else:
            index_path = os.path.join(config.FAISS_INDEX_DIR, "index_global.faiss")
            ids_path = os.path.join(config.FAISS_INDEX_DIR, "ids_global.json")
        
        faiss.write_index(index, index_path)
        with open(ids_path, 'w') as f:
            json.dump(chunk_ids, f)
    
    def load_faiss_index(self, pdf_id: int = None) -> Tuple[Optional[faiss.Index], List[int]]:
        """Load FAISS index from disk"""
        if pdf_id:
            index_path = os.path.join(config.FAISS_INDEX_DIR, f"index_{pdf_id}.faiss")
            ids_path = os.path.join(config.FAISS_INDEX_DIR, f"ids_{pdf_id}.json")
        else:
            index_path = os.path.join(config.FAISS_INDEX_DIR, "index_global.faiss")
            ids_path = os.path.join(config.FAISS_INDEX_DIR, "ids_global.json")
        
        if not os.path.exists(index_path):
            return None, []
        
        index = faiss.read_index(index_path)
        with open(ids_path, 'r') as f:
            chunk_ids = json.load(f)
        
        return index, chunk_ids
    
    def search_similar(self, query_embedding: np.ndarray, index: faiss.Index, 
                      chunk_ids: List[int], k: int = 3) -> List[int]:
        """Search for similar chunks"""
        if index is None or index.ntotal == 0:
            return []
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = index.search(query_embedding, k)
        
        result_chunk_ids = []
        for idx in indices[0]:
            if idx < len(chunk_ids):
                result_chunk_ids.append(chunk_ids[idx])
        
        return result_chunk_ids

