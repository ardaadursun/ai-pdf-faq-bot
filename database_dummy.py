"""
Dummy Database - In-Memory Storage
Replaces Oracle DB with simple in-memory data structures
"""

class DummyDB:
    """Simple in-memory database replacement"""
    
    def __init__(self):
        self.users = {}  # {user_id: {username, password_hash, created_at}}
        self.pdf_files = {}  # {pdf_id: {user_id, filename, upload_date}}
        self.chunks = {}  # {chunk_id: {pdf_id, text_chunk, chunk_index, page_number}}
        self.embeddings = {}  # {embedding_id: {chunk_id, vector}}
        self.queries = {}  # {query_id: {user_id, question, asked_at}}
        self.responses = {}  # {response_id: {query_id, answer, source_pdf, source_page, answered_at}}
        self.error_logs = []  # List of error dicts
        
        # Auto-increment counters
        self.user_id_counter = 1
        self.pdf_id_counter = 1
        self.chunk_id_counter = 1
        self.embedding_id_counter = 1
        self.query_id_counter = 1
        self.response_id_counter = 1
    
    def insert_user(self, username: str, password_hash: str) -> int:
        """Insert user and return user_id"""
        user_id = self.user_id_counter
        self.user_id_counter += 1
        self.users[user_id] = {
            'username': username,
            'password_hash': password_hash,
            'created_at': self._now()
        }
        return user_id
    
    def get_user_by_username(self, username: str) -> dict:
        """Get user by username"""
        for user_id, user_data in self.users.items():
            if user_data['username'] == username:
                return {'user_id': user_id, **user_data}
        return None
    
    def get_user_by_credentials(self, username: str, password_hash: str) -> dict:
        """Get user by username and password hash"""
        user = self.get_user_by_username(username)
        if user and user['password_hash'] == password_hash:
            return user
        return None
    
    def user_exists(self, username: str) -> bool:
        """Check if username exists"""
        return self.get_user_by_username(username) is not None
    
    def insert_pdf(self, user_id: int, filename: str) -> int:
        """Insert PDF and return pdf_id"""
        pdf_id = self.pdf_id_counter
        self.pdf_id_counter += 1
        self.pdf_files[pdf_id] = {
            'user_id': user_id,
            'filename': filename,
            'upload_date': self._now()
        }
        return pdf_id
    
    def get_pdfs_by_user(self, user_id: int) -> list:
        """Get all PDFs for a user"""
        result = []
        for pdf_id, pdf_data in self.pdf_files.items():
            if pdf_data['user_id'] == user_id:
                result.append((pdf_id, pdf_data['filename'], pdf_data['upload_date']))
        return sorted(result, key=lambda x: x[2], reverse=True)  # Sort by date desc
    
    def insert_chunk(self, pdf_id: int, text_chunk: str, chunk_index: int, page_number: int = None) -> int:
        """Insert chunk and return chunk_id"""
        chunk_id = self.chunk_id_counter
        self.chunk_id_counter += 1
        self.chunks[chunk_id] = {
            'pdf_id': pdf_id,
            'text_chunk': text_chunk,
            'chunk_index': chunk_index,
            'page_number': page_number
        }
        return chunk_id
    
    def get_chunks_by_pdf(self, pdf_id: int) -> list:
        """Get all chunks for a PDF, ordered by chunk_index"""
        result = []
        for chunk_id, chunk_data in self.chunks.items():
            if chunk_data['pdf_id'] == pdf_id:
                result.append((chunk_id, chunk_data))
        return sorted(result, key=lambda x: x[1]['chunk_index'])
    
    def get_chunk_by_id(self, chunk_id: int) -> dict:
        """Get chunk by ID"""
        if chunk_id in self.chunks:
            return {'chunk_id': chunk_id, **self.chunks[chunk_id]}
        return None
    
    def get_chunk_with_pdf_info(self, chunk_id: int) -> dict:
        """Get chunk with PDF filename"""
        chunk = self.get_chunk_by_id(chunk_id)
        if chunk:
            pdf_id = chunk['pdf_id']
            if pdf_id in self.pdf_files:
                chunk['filename'] = self.pdf_files[pdf_id]['filename']
            return chunk
        return None
    
    def insert_embedding(self, chunk_id: int, vector) -> int:
        """Insert embedding and return embedding_id"""
        embedding_id = self.embedding_id_counter
        self.embedding_id_counter += 1
        self.embeddings[embedding_id] = {
            'chunk_id': chunk_id,
            'vector': vector
        }
        return embedding_id
    
    def get_embeddings_by_pdf(self, pdf_id: int = None) -> list:
        """Get all embeddings, optionally filtered by pdf_id"""
        result = []
        for embedding_id, embedding_data in self.embeddings.items():
            chunk_id = embedding_data['chunk_id']
            chunk = self.get_chunk_by_id(chunk_id)
            if pdf_id is None or (chunk and chunk['pdf_id'] == pdf_id):
                result.append((embedding_id, chunk_id, embedding_data['vector']))
        return result
    
    def insert_query(self, user_id: int, question: str) -> int:
        """Insert query and return query_id"""
        query_id = self.query_id_counter
        self.query_id_counter += 1
        self.queries[query_id] = {
            'user_id': user_id,
            'question': question,
            'asked_at': self._now()
        }
        return query_id
    
    def get_latest_query(self, user_id: int, question: str) -> int:
        """Get latest query ID for user and question"""
        for query_id in sorted(self.queries.keys(), reverse=True):
            query_data = self.queries[query_id]
            if query_data['user_id'] == user_id and query_data['question'] == question:
                return query_id
        return None
    
    def insert_response(self, query_id: int, answer: str, source_pdf: str = None, source_page: int = None) -> int:
        """Insert response and return response_id"""
        response_id = self.response_id_counter
        self.response_id_counter += 1
        self.responses[response_id] = {
            'query_id': query_id,
            'answer': answer,
            'source_pdf': source_pdf,
            'source_page': source_page,
            'answered_at': self._now()
        }
        return response_id
    
    def log_error(self, message: str, stacktrace: str = None):
        """Log error"""
        self.error_logs.append({
            'message': message,
            'stacktrace': stacktrace,
            'created_at': self._now()
        })
    
    def _now(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now()

# Global instance
db = DummyDB()

