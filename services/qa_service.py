import re
from typing import List, Tuple, Optional
from database_dummy import db
from models.embeddings import EmbeddingManager
import config

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class QAService:
    """Handles question-answering logic"""
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.openai_client = None
        if OPENAI_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            except Exception:
                self.openai_client = None
    
    def get_chunk_text(self, chunk_id: int) -> dict:
        """Get chunk text and metadata from database"""
        chunk = db.get_chunk_with_pdf_info(chunk_id)
        if chunk:
            return {
                'chunk_id': chunk['chunk_id'],
                'text': chunk['text_chunk'],
                'page_number': chunk.get('page_number'),
                'filename': chunk.get('filename')
            }
        return None
    
    def find_relevant_chunks(self, question: str, pdf_id: int = None, top_k: int = 5) -> List[dict]:
        """Find relevant chunks using FAISS similarity search"""
        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embedding(question)
        
        # Load or create FAISS index
        index, chunk_ids = self.embedding_manager.load_faiss_index(pdf_id)
        
        if index is None:
            # Create index if it doesn't exist
            index, chunk_ids = self.embedding_manager.create_faiss_index(pdf_id)
            if index is not None:
                self.embedding_manager.save_faiss_index(index, chunk_ids, pdf_id)
        
        if index is None or len(chunk_ids) == 0:
            return []
        
        # Search for similar chunks
        similar_chunk_ids = self.embedding_manager.search_similar(
            query_embedding, index, chunk_ids, k=top_k
        )
        
        # Get chunk texts
        relevant_chunks = []
        for chunk_id in similar_chunk_ids:
            chunk = self.get_chunk_text(chunk_id)
            if chunk:
                relevant_chunks.append(chunk)
        
        return relevant_chunks
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from text using pattern matching"""
        # Email pattern: word characters, @, domain
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0).strip()
        return None
    
    def _extract_address(self, text: str) -> str:
        """Extract address from text using pattern matching"""
        # Pattern: Street name + number, then PLZ + City
        # Look for patterns like "Musterstraße 123, 12345 Musterstadt"
        address_pattern = r'([A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|weg|platz|allee|ring|gasse|damm|ufer)\s+\d+[a-z]?[,\s]+)?(\d{5})\s+([A-ZÄÖÜ][a-zäöüß]+(?:stadt|dorf|hausen)?)'
        match = re.search(address_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        
        # Simpler pattern: just street + number
        street_pattern = r'[A-ZÄÖÜ][a-zäöüß]+(?:straße|str\.|weg|platz|allee|ring|gasse|damm|ufer)\s+\d+[a-z]?'
        match = re.search(street_pattern, text, re.IGNORECASE)
        if match:
            # Try to get surrounding context (PLZ + City if nearby)
            start = match.start()
            end = match.end()
            context = text[max(0, start-10):min(len(text), end+50)]
            return context.strip()
        
        return None
    
    def _extract_relevant_section(self, question: str, text: str) -> str:
        """Extract the most relevant section from text based on question"""
        question_lower = question.lower()
        text_lower = text.lower()
        
        # Special handling for email questions (prioritize over address)
        if any(word in question_lower for word in ['email', 'e-mail', 'mail', 'e-mail-adresse', 'email-adresse']):
            email = self._extract_email(text)
            if email:
                return email
        
        # Special handling for address questions
        if any(word in question_lower for word in ['adresse', 'wohne', 'wohnort', 'wohnhaft']) and 'email' not in question_lower:
            address = self._extract_address(text)
            if address:
                return address
        
        # Identify question type and keywords
        question_keywords = []
        if any(word in question_lower for word in ['adresse', 'wohne', 'wohnort', 'wohnhaft']):
            question_keywords = ['straße', 'str.', 'weg', 'platz', 'adresse', 'wohnort', 'wohne', 'wohnhaft', 'straße', 'strasse']
        elif any(word in question_lower for word in ['email', 'e-mail', 'mail']):
            question_keywords = ['@', 'email', 'e-mail', 'mail']
        elif any(word in question_lower for word in ['telefon', 'nummer', 'handy', 'mobil']):
            question_keywords = ['telefon', 'tel.', 'mobil', 'handy', '+49', '+43', '+41']
        elif any(word in question_lower for word in ['geburt', 'geboren', 'geburtstag']):
            question_keywords = ['geboren', 'geburt', 'geburtstag', 'geb.']
        elif any(word in question_lower for word in ['name', 'heiße', 'heißt']):
            question_keywords = ['name', 'vorname', 'nachname']
        elif any(word in question_lower for word in ['beruf', 'arbeit', 'stelle', 'position']):
            question_keywords = ['beruf', 'arbeit', 'position', 'stelle', 'tätigkeit']
        else:
            # General: extract sentences containing question words
            question_words = [w for w in question_lower.split() if len(w) > 3]
            question_keywords = question_words
        
        # Find sentences containing keywords
        sentences = re.split(r'[.!?]\s+', text)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence contains any keyword
            if any(keyword in sentence_lower for keyword in question_keywords):
                relevant_sentences.append(sentence.strip())
        
        # If we found relevant sentences, return them
        if relevant_sentences:
            answer = '. '.join(relevant_sentences[:3])  # Max 3 sentences
            if not answer.endswith(('.', '!', '?')):
                answer += '.'
            return answer
        
        # Fallback: find the part of text with most keyword matches
        words = text.split()
        best_start = 0
        best_score = 0
        
        for i in range(len(words) - 10):
            window = ' '.join(words[i:i+20]).lower()
            score = sum(1 for keyword in question_keywords if keyword in window)
            if score > best_score:
                best_score = score
                best_start = i
        
        if best_score > 0:
            extracted = ' '.join(words[best_start:best_start+30])
            if len(extracted) > 200:
                extracted = extracted[:200] + '...'
            return extracted
        
        # Last resort: return first part of text
        if len(text) > 300:
            return text[:300] + '...'
        return text
    
    def _detect_question_type(self, question: str) -> str:
        """Detect what type of information is being asked"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['email', 'e-mail', 'mail', 'e-mail-adresse', 'email-adresse']):
            return "email"
        elif any(word in question_lower for word in ['adresse', 'wohne', 'wohnort', 'wohnhaft', 'anschrift']) and 'email' not in question_lower:
            return "address"
        elif any(word in question_lower for word in ['telefon', 'nummer', 'handy', 'mobil', 'tel']):
            return "phone"
        elif any(word in question_lower for word in ['geburt', 'geboren', 'geburtstag', 'alter']):
            return "birthdate"
        elif any(word in question_lower for word in ['name', 'heiße', 'heißt', 'vorname', 'nachname']):
            return "name"
        elif any(word in question_lower for word in ['beruf', 'arbeit', 'stelle', 'position', 'tätigkeit']):
            return "profession"
        else:
            return "general"
    
    def _generate_answer_with_openai(self, question: str, relevant_chunks: List[dict]) -> Optional[Tuple[str, Optional[str], Optional[int]]]:
        """Generate answer using OpenAI API"""
        if not self.openai_client:
            return None
        
        try:
            # Use more chunks for better context (up to 5)
            context_parts = []
            for chunk in relevant_chunks[:5]:
                context_parts.append(chunk['text'])
            
            context = "\n\n".join(context_parts)
            
            # Detect question type for better instructions
            question_type = self._detect_question_type(question)
            
            # Create specific instructions based on question type
            type_instructions = {
                "email": "Extrahiere NUR die E-Mail-Adresse. Suche nach Mustern wie name@domain.com. Gib nur die E-Mail-Adresse zurück, nichts anderes.",
                "address": "Extrahiere NUR die Adresse (Straße, Hausnummer, PLZ, Ort). Gib nur die vollständige Adresse zurück.",
                "phone": "Extrahiere NUR die Telefonnummer. Gib nur die Nummer zurück, nichts anderes.",
                "birthdate": "Extrahiere NUR das Geburtsdatum. Gib nur das Datum zurück.",
                "name": "Extrahiere NUR den Namen. Gib nur Vor- und Nachname zurück.",
                "profession": "Extrahiere NUR die Berufsbezeichnung oder Position. Gib nur diese Information zurück.",
                "general": "Antworte präzise und kurz. Extrahiere nur die relevante Information, die die Frage beantwortet."
            }
            
            instruction = type_instructions.get(question_type, type_instructions["general"])
            
            # Create improved prompt
            prompt = f"""Du analysierst ein Dokument und beantwortest Fragen präzise.

Dokumenteninhalt:
{context}

Frage: {question}

Anweisung: {instruction}

WICHTIG:
- Suche gezielt nach der gesuchten Information im Dokumenteninhalt
- Gib NUR die direkte Antwort zurück, keine Erklärungen
- Wenn die Information nicht im Dokument steht, antworte: "Nicht im Dokument enthalten"
- Sei präzise und kurz"""

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Du bist ein präziser Dokumenten-Assistent. Du extrahierst gezielt spezifische Informationen aus Dokumenten und gibst nur die direkte Antwort zurück."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more precise answers
                max_tokens=200  # Shorter answers for specific info
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Clean up answer - remove quotes if present
            if answer.startswith('"') and answer.endswith('"'):
                answer = answer[1:-1]
            if answer.startswith("'") and answer.endswith("'"):
                answer = answer[1:-1]
            
            # Use first chunk for source info
            best_chunk = relevant_chunks[0]
            source_pdf = best_chunk['filename']
            source_page = best_chunk['page_number']
            
            return answer, source_pdf, source_page
            
        except Exception as e:
            # If OpenAI fails, return None to fall back to local method
            print(f"OpenAI API Error: {e}")
            return None
    
    def generate_answer(self, question: str, relevant_chunks: List[dict]) -> Tuple[str, Optional[str], Optional[int]]:
        """
        Generate answer from relevant chunks
        Returns: (answer, source_pdf, source_page)
        """
        if not relevant_chunks:
            return "Nicht im Dokument enthalten", None, None
        
        # Try OpenAI first if available
        if self.openai_client:
            openai_result = self._generate_answer_with_openai(question, relevant_chunks)
            if openai_result:
                return openai_result
        
        # Fallback to local extraction method
        # Try to find answer in chunks, starting with most relevant
        best_answer = None
        best_chunk = relevant_chunks[0]
        
        for chunk in relevant_chunks:
            chunk_text = chunk['text']
            extracted = self._extract_relevant_section(question, chunk_text)
            
            # Check if extracted answer is meaningful (not just random text)
            question_lower = question.lower()
            extracted_lower = extracted.lower()
            
            # If extracted text contains question keywords, it's likely relevant
            question_words = [w for w in question_lower.split() if len(w) > 3]
            if any(word in extracted_lower for word in question_words) or len(extracted) < 100:
                best_answer = extracted
                best_chunk = chunk
                break
        
        # If no good match found, use first chunk
        if best_answer is None:
            best_chunk = relevant_chunks[0]
            best_answer = self._extract_relevant_section(question, best_chunk['text'])
        
        # Clean up answer
        answer = best_answer.strip()
        if len(answer) > 500:
            answer = answer[:500] + "..."
        
        source_pdf = best_chunk['filename']
        source_page = best_chunk['page_number']
        
        return answer, source_pdf, source_page
    
    def ask_question(self, question: str, user_id: int, pdf_id: int = None) -> dict:
        """Main Q&A method"""
        # Save query
        query_id = db.insert_query(user_id, question)
        
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question, pdf_id)
        
        # Generate answer
        answer, source_pdf, source_page = self.generate_answer(question, relevant_chunks)
        
        # Save response
        if query_id:
            db.insert_response(query_id, answer, source_pdf, source_page)
        
        return {
            'answer': answer,
            'source_pdf': source_pdf,
            'source_page': source_page,
            'relevant_chunks': len(relevant_chunks)
        }

