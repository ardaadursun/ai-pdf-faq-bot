import PyPDF2
import io
from typing import List, Tuple
import config

class PDFProcessor:
    """Handles PDF text extraction and chunking"""
    
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to split at sentence boundary
            chunk = text[start:end]
            last_period = max(
                chunk.rfind('. '),
                chunk.rfind('.\n'),
                chunk.rfind('! '),
                chunk.rfind('? ')
            )
            
            if last_period > self.chunk_size * 0.5:  # Only if we're past halfway
                end = start + last_period + 1
                chunk = text[start:end]
            
            chunks.append(chunk)
            
            # Move start forward with overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = end
        
        return chunks
    
    def extract_text_from_pdf(self, pdf_file) -> List[Tuple[str, int]]:
        """
        Extract text from PDF with page numbers
        Returns: List of (text, page_number) tuples
        """
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pages_text = []
        
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                pages_text.append((text, page_num))
        
        return pages_text
    
    def chunk_text(self, text: str, page_number: int = None) -> List[dict]:
        """
        Split text into chunks
        Returns: List of chunk dicts with text and metadata
        """
        chunks = self._split_text(text)
        chunk_list = []
        
        for idx, chunk_text in enumerate(chunks):
            chunk_dict = {
                'text': chunk_text,
                'chunk_index': idx,
                'page_number': page_number
            }
            chunk_list.append(chunk_dict)
        
        return chunk_list
    
    def process_pdf(self, pdf_file) -> List[dict]:
        """
        Process PDF: extract text and create chunks
        Returns: List of chunks with text and page numbers
        """
        pages = self.extract_text_from_pdf(pdf_file)
        all_chunks = []
        
        for page_text, page_num in pages:
            chunks = self.chunk_text(page_text, page_num)
            all_chunks.extend(chunks)
        
        return all_chunks

