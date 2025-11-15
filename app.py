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
    page_icon="🤖"
)

# Custom CSS with animations and modern design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Login Page Styling */
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.6s ease-out;
        margin: 2rem auto;
        max-width: 500px;
    }
    
    /* Main App Container */
    .main-app-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        animation: fadeIn 0.5s ease-out;
        margin: 1rem 0;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    /* Title Styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        animation: fadeInUp 0.6s ease-out;
    }
    
    h2, h3 {
        color: #2d3748;
        font-weight: 600;
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        animation: fadeIn 0.5s ease-out;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary Button */
    button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        animation: pulse 2s infinite;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.8);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
        font-weight: 600;
        box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Form Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* File Uploader */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 15px;
        padding: 2rem;
        border: 2px dashed #cbd5e0;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stFileUploader:hover {
        border-color: #667eea;
        background: rgba(255, 255, 255, 0.8);
    }
    
    /* Chat Messages */
    .stChatMessage {
        animation: slideIn 0.4s ease-out;
        margin-bottom: 1rem;
    }
    
    .stChatMessage[data-testid="user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 1rem;
        margin-left: 20%;
    }
    
    .stChatMessage[data-testid="assistant"] {
        background: #f7fafc;
        border-radius: 18px 18px 18px 4px;
        padding: 1rem;
        margin-right: 20%;
        border: 1px solid #e2e8f0;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .stError {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
    }
    
    /* PDF Cards */
    .pdf-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
        border-left: 4px solid #667eea;
    }
    
    .pdf-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
    }
    
    /* Spinner Animation */
    .stSpinner > div {
        border-top-color: #667eea;
        border-right-color: #764ba2;
    }
    
    /* Chat Input */
    .stChatInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Loading Animation */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        border: 3px solid rgba(102, 126, 234, 0.1);
        border-top-color: #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
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
        st.title("🤖 PDF FAQ Bot")
        st.markdown("### Willkommen zurück!")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔐 Login", "✨ Registrierung"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("#### Anmelden")
                username = st.text_input("👤 Benutzername", placeholder="Dein Benutzername")
                password = st.text_input("🔒 Passwort", type="password", placeholder="Dein Passwort")
                submit = st.form_submit_button("🚀 Einloggen", use_container_width=True)
                
                if submit:
                    user_id = user_service.authenticate_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("✅ Erfolgreich eingeloggt!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Ungültige Anmeldedaten!")
        
        with tab2:
            with st.form("register_form"):
                st.markdown("#### Neuen Account erstellen")
                new_username = st.text_input("👤 Neuer Benutzername", placeholder="Wähle einen Benutzernamen")
                new_password = st.text_input("🔒 Neues Passwort", type="password", placeholder="Sicheres Passwort")
                confirm_password = st.text_input("🔒 Passwort bestätigen", type="password", placeholder="Passwort wiederholen")
                submit = st.form_submit_button("✨ Registrieren", use_container_width=True)
                
                if submit:
                    if new_password != confirm_password:
                        st.error("❌ Passwörter stimmen nicht überein!")
                    elif user_service.user_exists(new_username):
                        st.error("❌ Benutzername bereits vergeben!")
                    else:
                        user_id = user_service.create_user(new_username, new_password)
                        st.session_state.user_id = user_id
                        st.session_state.username = new_username
                        st.success("🎉 Registrierung erfolgreich!")
                        st.balloons()
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    st.markdown('<div class="main-app-container">', unsafe_allow_html=True)
    
    # Header with gradient title
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 PDF FAQ Bot")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Abmelden", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    st.sidebar.title(f"👋 Willkommen, {st.session_state.username}")
    st.sidebar.markdown("---")
    
    # Get user's PDFs
    pdfs = db.get_pdfs_by_user(st.session_state.user_id)
    
    tab1, tab2 = st.tabs(["📤 PDFs hochladen", "💬 Fragen stellen"])
    
    with tab1:
        st.header("📤 PDF hochladen")
        st.markdown("Lade deine PDF-Dokumente hoch und lass sie automatisch verarbeiten.")
        
        uploaded_files = st.file_uploader(
            "📎 Wähle PDF-Dateien aus",
            type=['pdf'],
            accept_multiple_files=True,
            help="Du kannst mehrere PDFs gleichzeitig hochladen"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("⚡ PDFs verarbeiten", type="primary", use_container_width=True):
                if uploaded_files:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"🔄 Verarbeite {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
                        process_pdf(uploaded_file, st.session_state.user_id)
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_text.empty()
                    progress_bar.empty()
                    st.success(f"✅ {len(uploaded_files)} PDF(s) erfolgreich verarbeitet!")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("⚠️ Bitte wähle zuerst PDF-Dateien aus!")
        
        # Show uploaded PDFs with cards
        if pdfs:
            st.subheader("📚 Deine PDFs")
            for idx, (pdf_id, filename, upload_date) in enumerate(pdfs):
                st.markdown(f"""
                <div class="pdf-card">
                    <h4>📄 {filename}</h4>
                    <p style="color: #718096; margin: 0;">📅 Hochgeladen: {upload_date}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Noch keine PDFs hochgeladen. Lade deine ersten Dokumente hoch!")
    
    with tab2:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.header("💬 Chat mit deinen PDFs")
            st.markdown("Stelle Fragen zu deinen hochgeladenen Dokumenten und erhalte präzise Antworten.")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Chat löschen", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        # PDF selection
        if pdfs:
            pdf_options = ["📚 Alle PDFs"] + [f"📄 {filename}" for pdf_id, filename, _ in pdfs]
            selected_pdf = st.selectbox("📋 PDF auswählen", pdf_options, key="pdf_selector")
            
            selected_pdf_id = None
            if selected_pdf != "📚 Alle PDFs":
                # Find the matching PDF ID
                for pdf_id, filename, _ in pdfs:
                    if f"📄 {filename}" == selected_pdf:
                        selected_pdf_id = pdf_id
                        break
        else:
            st.warning("⚠️ Bitte lade zuerst PDFs hoch, bevor du Fragen stellst!")
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
                        st.caption(f"📄 **Quelle:** {chat_item['source_pdf']} | 📑 **Seite:** {chat_item['source_page']}")
        else:
            st.info("👋 Stelle deine erste Frage, um zu beginnen! Der Bot wird in deinen PDFs nach Antworten suchen.")
        
        # Question input at the bottom (chat style)
        question = st.chat_input("💭 Stelle eine Frage zu deinen PDFs...")
        
        if question:
            # Add user question to chat
            with st.chat_message("user"):
                st.markdown(f"**{question}**")
            
            # Get answer
            with st.chat_message("assistant"):
                with st.spinner("🤔 Denke nach..."):
                    result = qa_service.ask_question(question, st.session_state.user_id, selected_pdf_id)
                
                # Display answer with streaming animation
                _stream_text(result['answer'])
                
                if result['source_pdf']:
                    st.caption(f"📄 **Quelle:** {result['source_pdf']} | 📑 **Seite:** {result['source_page']}")
                
                if result['relevant_chunks'] == 0:
                    st.warning("⚠️ Keine relevanten Stellen in den Dokumenten gefunden. Versuche eine andere Formulierung.")
            
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

