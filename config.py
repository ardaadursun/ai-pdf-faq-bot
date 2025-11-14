import os
from dotenv import load_dotenv

load_dotenv()

# Embedding Model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# FAISS Index Directory
FAISS_INDEX_DIR = "faiss_indices"

# Chunking Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

