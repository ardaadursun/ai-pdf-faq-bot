import streamlit as st
import os
from database_dummy import db
from models.pdf_processor import PDFProcessor
from models.embeddings import EmbeddingManager
from services.user_service import UserService
from services.qa_service import QAService

# Page config
st.set_page_config(page_title="PDF FAQ Bot", layout="wide")

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
    st.title("PDF FAQ Bot")
    st.markdown("### Login oder Registrierung")
    
    tab1, tab2 = st.tabs(["Login", "Registrierung"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            submit = st.form_submit_button("Einloggen")
            
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
            new_username = st.text_input("Neuer Benutzername")
            new_password = st.text_input("Neues Passwort", type="password")
            confirm_password = st.text_input("Passwort bestätigen", type="password")
            submit = st.form_submit_button("Registrieren")
            
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

def show_main_app():
    st.title("PDF FAQ Bot")
    st.sidebar.title(f"Willkommen, {st.session_state.username}")
    
    if st.sidebar.button("Abmelden"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    # Get user's PDFs
    pdfs = db.get_pdfs_by_user(st.session_state.user_id)
    
    tab1, tab2 = st.tabs(["PDFs hochladen", "Fragen stellen"])
    
    with tab1:
        st.header("PDF hochladen")
        uploaded_files = st.file_uploader(
            "Wähle PDF-Dateien aus",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if st.button("PDFs verarbeiten", type="primary"):
            if uploaded_files:
                with st.spinner("PDFs werden verarbeitet..."):
                    for uploaded_file in uploaded_files:
                        process_pdf(uploaded_file, st.session_state.user_id)
                st.success(f"{len(uploaded_files)} PDF(s) erfolgreich verarbeitet!")
                st.rerun()
            else:
                st.warning("Bitte wähle zuerst PDF-Dateien aus!")
        
        # Show uploaded PDFs
        if pdfs:
            st.subheader("Deine PDFs")
            for pdf_id, filename, upload_date in pdfs:
                st.write(f"📄 {filename} (Hochgeladen: {upload_date})")
    
    with tab2:
        st.header("Fragen stellen")
        
        # PDF selection
        pdf_options = ["Alle PDFs"] + [f"{filename} (ID: {pdf_id})" for pdf_id, filename, _ in pdfs]
        selected_pdf = st.selectbox("PDF auswählen", pdf_options)
        
        selected_pdf_id = None
        if selected_pdf != "Alle PDFs":
            selected_pdf_id = int(selected_pdf.split("ID: ")[1].split(")")[0])
        
        # Question input
        question = st.text_input("Stelle eine Frage zu deinen PDFs")
        
        if st.button("Frage stellen", type="primary"):
            if question:
                with st.spinner("Suche nach Antwort..."):
                    result = qa_service.ask_question(question, st.session_state.user_id, selected_pdf_id)
                    
                    st.subheader("Antwort:")
                    st.write(result['answer'])
                    
                    if result['source_pdf']:
                        st.info(f"📄 Quelle: {result['source_pdf']}, Seite {result['source_page']}")
                    
                    if result['relevant_chunks'] == 0:
                        st.warning("Keine relevanten Stellen in den Dokumenten gefunden.")
            else:
                st.warning("Bitte gib eine Frage ein!")

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

