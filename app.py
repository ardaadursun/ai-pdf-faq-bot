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

# Custom CSS with animations and modern design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Ensure all text is visible - 100% Druckkraft */
    body, p, span, div, label {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Streamlit specific text elements - 100% Druckkraft */
    .stMarkdown, .stText, .stCaption {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Clean Professional Background */
    .stApp {
        background: #f8fafc;
        background-attachment: fixed;
    }
    
    /* Streamlit Header Menu - Weiße Schriften und Symbole */
    header[data-testid="stHeader"] {
        background: #1f2937 !important;
    }
    
    /* Header Menu Buttons and Text - Weiß */
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a,
    header[data-testid="stHeader"] span,
    header[data-testid="stHeader"] div,
    header[data-testid="stHeader"] p {
        color: white !important;
    }
    
    /* Header Icons - Weiß */
    header[data-testid="stHeader"] svg,
    header[data-testid="stHeader"] path {
        fill: white !important;
        stroke: white !important;
        color: white !important;
    }
    
    /* Header Menu Items - Weiß */
    header[data-testid="stHeader"] .stToolbar button,
    header[data-testid="stHeader"] .stToolbar a {
        color: white !important;
        fill: white !important;
    }
    
    /* Header Menu Hover */
    header[data-testid="stHeader"] button:hover,
    header[data-testid="stHeader"] a:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    /* Dropdown Menu - Dunkler Hintergrund, weiße Schrift */
    [data-baseweb="popover"] {
        background: #1f2937 !important;
    }
    
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] a,
    [data-baseweb="popover"] span,
    [data-baseweb="popover"] div {
        color: white !important;
    }
    
    [data-baseweb="popover"] li:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Share, Settings, etc. Menu Items */
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] a,
    [data-baseweb="menu"] span {
        color: white !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Spezifische Header-Elemente - Weiß */
    header[data-testid="stHeader"] [class*="share"],
    header[data-testid="stHeader"] [class*="menu"],
    header[data-testid="stHeader"] [class*="button"],
    header[data-testid="stHeader"] [class*="icon"] {
        color: white !important;
        fill: white !important;
    }
    
    /* Alle SVG-Elemente im Header - Weiß */
    header[data-testid="stHeader"] * svg,
    header[data-testid="stHeader"] * path,
    header[data-testid="stHeader"] * circle,
    header[data-testid="stHeader"] * rect {
        fill: white !important;
        stroke: white !important;
    }
    
    /* Text im Header - Weiß und kräftig */
    header[data-testid="stHeader"] * {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Login Page Styling */
    .login-container {
        background: white;
        backdrop-filter: none;
        border-radius: 16px;
        padding: 3rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        animation: fadeInUp 0.6s ease-out;
        margin: 2rem auto;
        max-width: 500px;
        border: 1px solid #e5e7eb;
    }
    
    /* Main App Container */
    .main-app-container {
        background: white;
        backdrop-filter: none;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        animation: fadeIn 0.5s ease-out;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    
    /* Main App Container - Alle Texte schwarz */
    .main-app-container h1,
    .main-app-container h2,
    .main-app-container h3,
    .main-app-container h4,
    .main-app-container p,
    .main-app-container span,
    .main-app-container div,
    .main-app-container label,
    .main-app-container * {
        color: #000000 !important;
    }
    
    /* Tabs im Main Container - Schwarz */
    .main-app-container .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
    }
    
    .main-app-container .stTabs [aria-selected="true"] {
        color: #2563eb !important;
    }
    
    /* File Uploader Label - Schwarz */
    .main-app-container .stFileUploader label,
    .main-app-container .stFileUploader span,
    .main-app-container .stFileUploader div {
        color: #000000 !important;
    }
    
    /* Info Messages im Main Container - Original Farben beibehalten */
    .main-app-container .stInfo {
        background: #dbeafe !important;
        color: #1e40af !important;
    }
    
    .main-app-container .stInfo p,
    .main-app-container .stInfo span,
    .main-app-container .stInfo div {
        color: #1e40af !important;
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
    
    /* Title Styling - 100% Druckkraft */
    h1 {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        animation: fadeInUp 0.6s ease-out;
        letter-spacing: -0.5px;
    }
    
    h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 800 !important;
        animation: fadeIn 0.5s ease-out;
        letter-spacing: -0.3px;
    }
    
    /* Paragraph and text styling - 100% Druckkraft */
    p {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Labels and captions - 100% Druckkraft */
    label, .stCaption {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Button Styling - 100% Druckkraft */
    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 700 !important;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        animation: fadeIn 0.5s ease-out;
        letter-spacing: 0.3px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        background: #1d4ed8;
    }
    
    .stButton > button:active {
        transform: translateY(0);
        background: #1e40af;
    }
    
    /* Primary Button */
    button[kind="primary"] {
        background: #2563eb !important;
        animation: pulse 2s infinite;
    }
    
    button[kind="primary"]:hover {
        background: #1d4ed8 !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f3f4f6;
        border-radius: 8px 8px 0 0;
        padding: 1rem 2rem;
        font-weight: 700 !important;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
        color: #000000 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e5e7eb;
        transform: translateY(-2px);
        color: #000000 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #2563eb !important;
        font-weight: 800 !important;
        box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
        border-bottom: 2px solid #2563eb;
    }
    
    /* Form Styling - 100% Druckkraft */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 0.75rem;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
        background: white;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }
    
    /* File Uploader */
    .stFileUploader {
        background: #f9fafb;
        border-radius: 12px;
        padding: 2rem;
        border: 2px dashed #d1d5db;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }
    
    .stFileUploader:hover {
        border-color: #2563eb;
        background: #f3f4f6;
    }
    
    /* Chat Messages */
    .stChatMessage {
        animation: slideIn 0.4s ease-out;
        margin-bottom: 1rem;
    }
    
    .stChatMessage[data-testid="user"] {
        background: #2563eb;
        color: white;
        border-radius: 16px 16px 4px 16px;
        padding: 1rem;
        margin-left: 20%;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    .stChatMessage[data-testid="assistant"] {
        background: #f9fafb;
        border-radius: 16px 16px 16px 4px;
        padding: 1rem;
        margin-right: 20%;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* Ensure chat message text is visible - 100% Druckkraft */
    .stChatMessage[data-testid="assistant"] p,
    .stChatMessage[data-testid="assistant"] div,
    .stChatMessage[data-testid="assistant"] span {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stChatMessage[data-testid="user"] p,
    .stChatMessage[data-testid="user"] div,
    .stChatMessage[data-testid="user"] span {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar Styling - Dunkler Hintergrund, weiße Schrift */
    .css-1d391kg {
        background: #1f2937 !important;
        backdrop-filter: none;
        border-right: 1px solid #374151;
    }
    
    /* Sidebar Container - Dunkel */
    [data-testid="stSidebar"] {
        background: #1f2937 !important;
    }
    
    /* Ensure sidebar text is visible - Weiß und kräftig */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] * {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar Separator - Hellgrau */
    [data-testid="stSidebar"] hr {
        border-color: #4b5563 !important;
    }
    
    /* Sidebar Icons - Weiß */
    [data-testid="stSidebar"] svg,
    [data-testid="stSidebar"] path,
    [data-testid="stSidebar"] circle,
    [data-testid="stSidebar"] rect {
        fill: white !important;
        stroke: white !important;
    }
    
    /* Streamlit App Label oben links - Weiß */
    [data-testid="stAppViewContainer"] [class*="appview"],
    [data-testid="stAppViewContainer"] [class*="label"],
    [data-testid="stAppViewContainer"] [class*="badge"],
    [data-testid="stAppViewContainer"] [class*="streamlitApp"] {
        background: #1f2937 !important;
        color: white !important;
    }
    
    /* Alle Elemente oben links - Weiß */
    [data-testid="stAppViewContainer"] > div:first-child,
    [data-testid="stAppViewContainer"] > div:first-child * {
        color: white !important;
    }
    
    /* Spezifisch für das App-Label */
    div[class*="appview"] [class*="badge"],
    div[class*="appview"] [class*="label"],
    div[class*="streamlitApp"] {
        background: #1f2937 !important;
        color: white !important;
        border-color: #4b5563 !important;
    }
    
    /* Alle Labels und Badges oben links - Weiß */
    [class*="badge"],
    [class*="label"][class*="app"],
    [class*="streamlitApp"] {
        background: #1f2937 !important;
        color: white !important;
        border-color: #4b5563 !important;
    }
    
    /* Universeller Selektor für alle Elemente oben links */
    .stApp > div:first-child,
    .stApp > div:first-child *,
    [data-testid="stAppViewContainer"] > div:first-child * {
        color: white !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: #d1fae5;
        color: #065f46;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
        border: 1px solid #a7f3d0;
    }
    
    .stError {
        background: #fee2e2;
        color: #991b1b;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
        border: 1px solid #fecaca;
    }
    
    .stWarning {
        background: #fef3c7;
        color: #92400e;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
        border: 1px solid #fde68a;
    }
    
    .stInfo {
        background: #dbeafe;
        color: #1e40af !important;
        border-radius: 8px;
        padding: 1rem;
        animation: fadeInUp 0.5s ease-out;
        border: 1px solid #93c5fd;
    }
    
    /* Ensure info/warning/error text is visible - 100% Druckkraft */
    .stInfo p, .stInfo div, .stInfo span {
        color: #1e40af !important;
        font-weight: 700 !important;
    }
    
    .stWarning p, .stWarning div, .stWarning span {
        color: #92400e !important;
        font-weight: 700 !important;
    }
    
    .stSuccess p, .stSuccess div, .stSuccess span {
        color: #065f46 !important;
        font-weight: 700 !important;
    }
    
    .stError p, .stError div, .stError span {
        color: #991b1b !important;
        font-weight: 700 !important;
    }
    
    /* PDF Cards */
    .pdf-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #2563eb;
    }
    
    .pdf-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-color: #2563eb;
    }
    
    /* Ensure PDF card text is visible - 100% Druckkraft */
    .pdf-card p, .pdf-card h4, .pdf-card div, .pdf-card span {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    .pdf-card h4 {
        font-weight: 800 !important;
    }
    
    /* Selectbox Styling - 100% Druckkraft */
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        transition: all 0.3s ease;
        background: white;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }
    
    /* Spinner Animation */
    .stSpinner > div {
        border-top-color: #2563eb;
        border-right-color: #3b82f6;
    }
    
    /* Chat Input - 100% Druckkraft */
    .stChatInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stChatInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f3f4f6;
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #9ca3af;
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6b7280;
    }
    
    /* Loading Animation */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        border: 3px solid rgba(37, 99, 235, 0.1);
        border-top-color: #2563eb;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    /* ============================================
       LOGIN CONTAINER - HÖCHSTE PRIORITÄT
       Alle Texte müssen schwarz sein!
       ============================================ */
    
    /* Überschreibe ALLE Styles für Login Container - Sehr spezifisch */
    div.login-container,
    div.login-container *,
    .login-container,
    .login-container * {
        color: #000000 !important;
    }
    
    /* Überschreibe spezifisch für alle Elemente */
    .login-container h1,
    .login-container h2,
    .login-container h3,
    .login-container h4,
    .login-container h5,
    .login-container h6,
    .login-container p,
    .login-container span,
    .login-container div,
    .login-container label,
    .login-container a,
    .login-container button {
        color: #000000 !important;
    }
    
    /* Streamlit Widgets im Login Container */
    .login-container .stMarkdown,
    .login-container .stMarkdown *,
    .login-container .stText,
    .login-container .stText *,
    .login-container .stCaption,
    .login-container .stCaption *,
    .login-container [class*="stMarkdown"],
    .login-container [class*="stMarkdown"] * {
        color: #000000 !important;
    }
    
    /* Tabs - Schwarz, außer aktiver Tab */
    .login-container .stTabs [data-baseweb="tab"],
    .login-container .stTabs [data-baseweb="tab"] *,
    .login-container .stTabs [data-baseweb="tab"] span {
        color: #000000 !important;
    }
    
    .login-container .stTabs [aria-selected="true"],
    .login-container .stTabs [aria-selected="true"] * {
        color: #2563eb !important;
    }
    
    /* Form Labels - Schwarz */
    .login-container .stTextInput label,
    .login-container .stTextInput span,
    .login-container .stTextInput div,
    .login-container label,
    .login-container [class*="label"],
    .login-container [class*="Label"],
    .login-container [data-baseweb="label"] {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Input Placeholder - Grau */
    .login-container .stTextInput input::placeholder {
        color: #9ca3af !important;
    }
    
    /* Alle Streamlit Elemente - Schwarz */
    .login-container [data-testid],
    .login-container [data-testid] *,
    .login-container [class*="st"],
    .login-container [class*="st"] * {
        color: #000000 !important;
    }
    
    /* Überschreibe auch Baseweb Styles */
    .login-container [data-baseweb],
    .login-container [data-baseweb] * {
        color: #000000 !important;
    }
    
    /* Button Text bleibt weiß (für Buttons mit blauem Hintergrund) */
    .login-container .stButton > button {
        color: white !important;
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
                        st.balloons()
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
                        st.success(" Registrierung erfolgreich!")
                        st.balloons()
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
                    st.balloons()
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

