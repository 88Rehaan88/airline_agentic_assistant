# Central configuration file for models, retrieval settings, safety limits and index paths. 

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Models
CHAT_MODEL: str = "gpt-4o-mini" # cheap, fast, good for general queries
EMBED_MODEL: str = "text-embedding-3-small" 
RERANK_MODEL: str = "gpt-4o-mini"  # same model as chat, but used in a separate reranking call
NUMERIC_MODEL: str = "gpt-4o"      # stronger model for numeric table selection and value extraction

# Retrieval — FAISS fetches a wider pool first, then the reranker trims it down
RERANK_TOP_K: int = 2   # chunks kept after reranking (what the agent actually sees)
FAISS_FETCH_K: int = 8  # # Initial number of chunks retrieved from FAISS before sending it to the reranker

# Prevents infinite tool-calling loops 
MAX_ITERATIONS: int = 10

# Index is built once offline and loaded at runtime
INDEX_DIR: str = "index"
FAISS_INDEX_PATH: str = f"{INDEX_DIR}/faiss.index"  
CHUNKS_PATH: str = f"{INDEX_DIR}/chunks.json" # Metadata file storing chunk text + page mapping
TABLES_PATH: str = f"{INDEX_DIR}/tables.json" # Raw pdfplumber tables per page, used by the numeric query path
