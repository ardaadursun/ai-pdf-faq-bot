import streamlit as st
import os
from database_dummy import db
from models.pdf_processor import PDFProcessor
from models.embeddings import EmbeddingManager
from services.user_service import UserService
from services.qa_service import QAService

# Page config
st.set_page_config(
    page_title="PDF FAQ Bot", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=None
)

# Custom CSS - Fresh Clean Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main App Background - White */
    .stApp {
        background: #ffffff;
    }
    
    /* Main Content Area - White Background, Black Text */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: #ffffff;
    }
    
    .main .block-container * {
        color: #000000 !important;
    }
    
    /* Header - Dark Background, White Text */
    header[data-testid="stHeader"] {
        background: #1a1a1a !important;
    }
    
    header[data-testid="stHeader"] * {
        color: #ffffff !important;
    }
    
    header[data-testid="stHeader"] svg,
    header[data-testid="stHeader"] path {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    /* Dropdown Menus - Dark Background, White Text */
    [data-baseweb="popover"] {
        background: #1a1a1a !important;
    }
    
    [data-baseweb="popover"] * {
        color: #ffffff !important;
    }
    
    [data-baseweb="menu"] * {
        color: #ffffff !important;
    }
    
    /* Sidebar - Dark Background, White Text */
    [data-testid="stSidebar"] {
        background: #1a1a1a !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] svg,
    [data-testid="stSidebar"] path {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #404040 !important;
    }
    
    /* Login Container - White Background, Black Text */
    .login-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 3rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.5s ease-out;
        margin: 2rem auto;
        max-width: 500px;
        border: 1px solid #e0e0e0;
    }
    
    .login-container * {
        color: #000000 !important;
    }
    
    /* Main App Container - White Background, Black Text */
    .main-app-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        animation: fadeIn 0.5s ease-out;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .main-app-container * {
        color: #000000 !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Typography - Black Text on White */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 600;
        animation: fadeIn 0.5s ease-out;
    }
    
    p, span, div, label {
        color: #000000 !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: #000000;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        transition: all 0.2s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stButton > button:hover {
        background: #333333;
        transform: translateY(-1px);
    }
    
    button[kind="primary"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    button[kind="primary"]:hover {
        background: #333333 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background: #f5f5f5;
        border-radius: 8px 8px 0 0;
        padding: 1rem 2rem;
        font-weight: 500;
        transition: all 0.2s ease;
        animation: fadeIn 0.5s ease-out;
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e8e8e8;
    }
    
    .stTabs [aria-selected="true"] {
        background: #ffffff;
        color: #000000 !important;
        font-weight: 600;
        border-bottom: 2px solid #000000;
    }
    
    /* Form Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #d0d0d0;
        padding: 0.75rem;
        transition: all 0.2s ease;
        animation: fadeIn 0.5s ease-out;
        background: #ffffff;
        color: #000000 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #000000;
        outline: none;
        box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
    }
    
    /* File Uploader */
    .stFileUploader {
        background: #f9f9f9;
        border-radius: 12px;
        padding: 2rem;
        border: 2px dashed #d0d0d0;
        transition: all 0.2s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stFileUploader:hover {
        border-color: #000000;
        background: #f5f5f5;
    }
    
    .stFileUploader * {
        color: #000000 !important;
    }
    
    /* Chat Messages */
    .stChatMessage {
        animation: slideIn 0.3s ease-out;
        margin-bottom: 1rem;
    }
    
    .stChatMessage[data-testid="user"] {
        background: #1a1a1a;
        color: #ffffff;
        border-radius: 16px 16px 4px 16px;
        padding: 1rem;
        margin-left: 20%;
    }
    
    .stChatMessage[data-testid="user"] * {
        color: #ffffff !important;
    }
    
    .stChatMessage[data-testid="assistant"] {
        background: #f5f5f5;
        border-radius: 16px 16px 16px 4px;
        padding: 1rem;
        margin-right: 20%;
        border: 1px solid #e0e0e0;
    }
    
    .stChatMessage[data-testid="assistant"] * {
        color: #000000 !important;
    }
    
    /* Chat Input */
    .stChatInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #d0d0d0;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.2s ease;
        background: #ffffff;
        color: #000000 !important;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #000000;
        outline: none;
        box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Selectbox */
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #d0d0d0;
        transition: all 0.2s ease;
        background: #ffffff;
        color: #000000 !important;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #000000;
        outline: none;
        box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Messages */
    .stSuccess {
        background: #e8f5e9;
        color: #2e7d32;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeIn 0.5s ease-out;
        border: 1px solid #c8e6c9;
    }
    
    .stSuccess * {
        color: #2e7d32 !important;
    }
    
    .stError {
        background: #ffebee;
        color: #c62828;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeIn 0.5s ease-out;
        border: 1px solid #ffcdd2;
    }
    
    .stError * {
        color: #c62828 !important;
    }
    
    .stWarning {
        background: #fff3e0;
        color: #e65100;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeIn 0.5s ease-out;
        border: 1px solid #ffe0b2;
    }
    
    .stWarning * {
        color: #e65100 !important;
    }
    
    .stInfo {
        background: #e3f2fd;
        color: #1565c0;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeIn 0.5s ease-out;
        border: 1px solid #bbdefb;
    }
    
    .stInfo * {
        color: #1565c0 !important;
    }
    
    /* PDF Cards */
    .pdf-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
        animation: fadeIn 0.5s ease-out;
        border: 1px solid #e0e0e0;
        border-left: 3px solid #000000;
    }
    
    .pdf-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .pdf-card * {
        color: #000000 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f5f5f5;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #b0b0b0;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #808080;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
user_service = UserService()
pdf_processor = PDFProcessor()
embedding_manager = EmbeddingManager()
qa_service = QAService()

# Session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

def main():
    if st.session_state.user_id is None:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    # Centered container with animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("PDF FAQ Bot")
        st.markdown("Willkommen zurück!")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Registrierung"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("#### Anmelden")
                username = st.text_input("Benutzername", placeholder="Dein Benutzername")
                password = st.text_input("Passwort", type="password", placeholder="Dein Passwort")
                submit = st.form_submit_button("Einloggen", use_container_width=True)
                
                if submit:
                    user_id = user_service.authenticate_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("Erfolgreich eingeloggt!")
                        st.rerun()
                    else:
                        st.error("Ungültige Anmeldedaten!")
        
        with tab2:
            with st.form("register_form"):
                st.markdown("#### Neuen Account erstellen")
                new_username = st.text_input("Neuer Benutzername", placeholder="Wähle einen Benutzernamen")
                new_password = st.text_input("Neues Passwort", type="password", placeholder="Sicheres Passwort")
                confirm_password = st.text_input("Passwort bestätigen", type="password", placeholder="Passwort wiederholen")
                submit = st.form_submit_button("Registrieren", use_container_width=True)
                
                if submit:
                    if new_password != confirm_password:
                        st.error("Passwörter stimmen nicht überein!")
                    elif user_service.user_exists(new_username):
                        st.error("Benutzername bereits vergeben!")
                    else:
                        user_id = user_service.create_user(new_username, new_password)
                        st.session_state.user_id = user_id
                        st.session_state.username = new_username
                        st.success("Registrierung erfolgreich!")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
    
    # Header with gradient title
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("PDF FAQ Bot")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    st.sidebar.title(f"Willkommen, {st.session_state.username}")
    st.sidebar.markdown("---")
    
    # Get user's PDFs
    pdfs = db.get_pdfs_by_user(st.session_state.user_id)
    
    tab1, tab2 = st.tabs(["PDFs hochladen", "Fragen stellen"])
    
    with tab1:
        st.header("PDF hochladen")
        st.markdown("Lade deine PDF-Dokumente hoch und lass sie automatisch verarbeiten.")
        
        uploaded_files = st.file_uploader(
            "Wähle PDF-Dateien aus",
            type=['pdf'],
            accept_multiple_files=True,
            help="Du kannst mehrere PDFs gleichzeitig hochladen"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("PDFs verarbeiten", type="primary", use_container_width=True):
                if uploaded_files:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Verarbeite {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
                        process_pdf(uploaded_file, st.session_state.user_id)
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_text.empty()
                    progress_bar.empty()
                    st.success(f"{len(uploaded_files)} PDF(s) erfolgreich verarbeitet!")
                    st.rerun()
                else:
                    st.warning("Bitte wähle zuerst PDF-Dateien aus!")
        
        # Show uploaded PDFs with cards
        if pdfs:
            st.subheader("Deine PDFs")
            for idx, (pdf_id, filename, upload_date) in enumerate(pdfs):
                st.markdown(f"""
                <div class="pdf-card">
                    <h4>{filename}</h4>
                    <p style="color: #718096; margin: 0;">Hochgeladen: {upload_date}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Noch keine PDFs hochgeladen. Lade deine ersten Dokumente hoch!")
    
    with tab2:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.header("Chat mit deinen PDFs")
            st.markdown("Stelle Fragen zu deinen hochgeladenen Dokumenten und erhalte präzise Antworten.")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Chat löschen", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        # PDF selection
        if pdfs:
            pdf_options = ["Alle PDFs"] + [filename for pdf_id, filename, _ in pdfs]
            selected_pdf = st.selectbox("PDF auswählen", pdf_options, key="pdf_selector")
            
            selected_pdf_id = None
            if selected_pdf != "Alle PDFs":
                # Find the matching PDF ID
                for pdf_id, filename, _ in pdfs:
                    if filename == selected_pdf:
                        selected_pdf_id = pdf_id
                        break
        else:
            st.warning("Bitte lade zuerst PDFs hoch, bevor du Fragen stellst!")
            selected_pdf_id = None
        
        # Initialize chat history in session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        if st.session_state.chat_history:
            for idx, chat_item in enumerate(st.session_state.chat_history):
                # Display question (user message)
                with st.chat_message("user"):
                    st.markdown(f"**{chat_item['question']}**")
                
                # Display answer (assistant message)
                with st.chat_message("assistant"):
                    st.markdown(chat_item['answer'])
                    if chat_item.get('source_pdf'):
                        st.caption(f"**Quelle:** {chat_item['source_pdf']} | **Seite:** {chat_item['source_page']}")
        else:
            st.info("Stelle deine erste Frage, um zu beginnen! Der Bot wird in deinen PDFs nach Antworten suchen.")
        
        # Question input at the bottom (chat style)
        question = st.chat_input("Stelle eine Frage zu deinen PDFs...")
        
        if question:
            # Add user question to chat
            with st.chat_message("user"):
                st.markdown(f"**{question}**")
            
            # Get answer
            with st.chat_message("assistant"):
                with st.spinner("Denke nach..."):
                    result = qa_service.ask_question(question, st.session_state.user_id, selected_pdf_id)
                
                # Display answer with streaming animation
                _stream_text(result['answer'])
                
                if result['source_pdf']:
                    st.caption(f"**Quelle:** {result['source_pdf']} | **Seite:** {result['source_page']}")
                
                if result['relevant_chunks'] == 0:
                    st.warning("Keine relevanten Stellen in den Dokumenten gefunden. Versuche eine andere Formulierung.")
            
            # Save to chat history
            st.session_state.chat_history.append({
                'question': question,
                'answer': result['answer'],
                'source_pdf': result['source_pdf'],
                'source_page': result['source_page']
            })
            
            # Scroll to bottom (rerun to show new message)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def _stream_text(text: str):
    """Display text with ChatGPT-like streaming animation"""
    import time
    placeholder = st.empty()
    
    # Split text into words
    words = text.split()
    displayed_text = ""
    
    for word in words:
        displayed_text += word + " "
        placeholder.markdown(displayed_text + "▌")  # Cursor effect
        time.sleep(0.015)  # Adjust speed here (lower = faster, 0.015 = ~67 words/sec)
    
    # Remove cursor at the end
    placeholder.markdown(displayed_text.strip())

def process_pdf(uploaded_file, user_id):
    """Process uploaded PDF: extract, chunk, embed, and save to DB"""
    try:
        # Save PDF info to DB
        pdf_id = db.insert_pdf(user_id, uploaded_file.name)
        
        if not pdf_id:
            return
        
        # Process PDF
        uploaded_file.seek(0)
        chunks = pdf_processor.process_pdf(uploaded_file)
        
        # Save chunks and generate embeddings
        chunk_texts = []
        chunk_ids = []
        for chunk in chunks:
            chunk_id = db.insert_chunk(
                pdf_id, 
                chunk['text'], 
                chunk['chunk_index'], 
                chunk.get('page_number')
            )
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk['text'])
        
        # Generate and save embeddings
        embeddings = embedding_manager.generate_embeddings_batch(chunk_texts)
        for chunk_id, embedding in zip(chunk_ids, embeddings):
            embedding_manager.save_embedding_to_db(chunk_id, embedding)
        
        # Create and save FAISS index
        index, chunk_ids_list = embedding_manager.create_faiss_index(pdf_id)
        if index is not None:
            embedding_manager.save_faiss_index(index, chunk_ids_list, pdf_id)
        
    except Exception as e:
        import traceback
        st.error(f"Fehler beim Verarbeiten von {uploaded_file.name}: {str(e)}")
        # Log error
        stacktrace = traceback.format_exc()
        db.log_error(str(e), stacktrace)

if __name__ == "__main__":
    main()

