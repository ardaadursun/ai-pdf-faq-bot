# AI PDF FAQ Bot

Ein intelligenter FAQ-Chatbot für PDF-Dokumente, der Fragen zu hochgeladenen Dokumenten beantwortet. Die Anwendung nutzt moderne NLP-Technologien für semantische Suche und präzise Antwortgenerierung.

##  Features

- **PDF-Verarbeitung**: Automatische Textextraktion und intelligentes Chunking
- **Semantische Suche**: FAISS-basierte Vektorsuche für präzise Treffer
- **Intelligente Antworten**: Kontextbewusste Extraktion relevanter Informationen
- **Quellenangaben**: Automatische Referenzierung von PDF und Seitenzahl
- **User Management**: Einfaches Login- und Registrierungssystem
- **In-Memory Storage**: Keine externe Datenbank erforderlich

##  Voraussetzungen

- Python 3.10 oder höher
- pip (Python Package Manager)

##  Installation

### 1. Repository klonen

```bash
git clone <repository-url>
cd "AI PDF FAQ Bot"
```

### 2. Virtuelle Umgebung erstellen

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

##  Verwendung

### App starten

```bash
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

### Workflow

1. **Registrierung/Login**: Erstelle einen neuen Account oder logge dich mit bestehenden Credentials ein
2. **PDF hochladen**: Lade ein oder mehrere PDF-Dokumente hoch (AGBs, Verträge, Rechnungen, Lebensläufe, etc.)
3. **Fragen stellen**: Stelle Fragen zu den hochgeladenen Dokumenten
4. **Antworten erhalten**: Erhalte präzise Antworten mit Quellenangaben

### Beispiel-Fragen

- "Was ist meine Adresse?"
- "Wie lautet meine E-Mail?"
- "Was steht in den AGBs zu Rückgabe?"
- "Welche Position habe ich in meinem Lebenslauf?"

##  Projektstruktur

```
AI PDF FAQ Bot/
├── app.py                 # Streamlit Frontend
├── config.py             # Konfiguration
├── database_dummy.py     # In-Memory Datenbank
├── models/
│   ├── __init__.py
│   ├── pdf_processor.py  # PDF Extraction & Chunking
│   └── embeddings.py     # Embeddings & FAISS Management
├── services/
│   ├── __init__.py
│   ├── qa_service.py     # Q&A Logik mit intelligenter Extraktion
│   └── user_service.py   # User Management
├── faiss_indices/        # Gespeicherte FAISS-Indizes
├── requirements.txt      # Python Dependencies
└── README.md             # Diese Datei
```

##  Technologie-Stack

- **Streamlit**: Web-Frontend
- **FAISS**: Vektorsuche für semantische Suche
- **Sentence Transformers**: HuggingFace Embeddings (all-MiniLM-L6-v2)
- **PyPDF2**: PDF-Text-Extraktion
- **NumPy**: Numerische Operationen

##  Konfiguration

Die Konfiguration erfolgt über `config.py`:

- **EMBEDDING_MODEL**: HuggingFace Modell für Embeddings (Standard: `sentence-transformers/all-MiniLM-L6-v2`)
- **CHUNK_SIZE**: Größe der Text-Chunks (Standard: 1000 Zeichen)
- **CHUNK_OVERLAP**: Overlap zwischen Chunks (Standard: 200 Zeichen)

Optional kann eine `.env` Datei erstellt werden:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

##  Funktionsweise

1. **PDF-Verarbeitung**: 
   - Text wird seitenweise extrahiert
   - Intelligentes Chunking an Satzgrenzen
   - Seitenzahlen werden gespeichert

2. **Embedding-Generierung**:
   - Jeder Chunk wird in einen Vektor umgewandelt
   - Embeddings werden im Speicher gespeichert

3. **FAISS-Index**:
   - Vektoren werden in einem FAISS-Index gespeichert
   - Index wird lokal für schnelle Suche gespeichert

4. **Frage-Antwort**:
   - Frage wird in einen Vektor umgewandelt
   - Semantische Suche findet relevante Chunks
   - Intelligente Extraktion der relevanten Informationen
   - Antwort wird mit Quellenangabe zurückgegeben

##  Hinweise

- **In-Memory Storage**: Alle Daten werden im Speicher gehalten und gehen beim Neustart verloren
- **FAISS-Indizes**: Werden lokal gespeichert und bleiben erhalten
- **Keine externe Datenbank**: Die App benötigt keine Oracle oder andere Datenbank
- **Embeddings**: Werden beim Neustart neu generiert

##  Fehlerbehebung

### App startet nicht

```bash
# Prüfe Python-Version
python3 --version  # Sollte 3.10+ sein

# Prüfe Dependencies
pip list | grep streamlit
```

### PDF wird nicht verarbeitet

- Stelle sicher, dass das PDF Text enthält (nicht nur Bilder)
- Prüfe die Fehlermeldungen in der App

### Keine Antworten gefunden

- Stelle sicher, dass PDFs hochgeladen wurden
- Verwende präzise Fragen
- Prüfe, ob die Frage im Dokument enthalten ist

##  Lizenz

Dieses Projekt ist für persönliche und kommerzielle Nutzung frei verfügbar.

##  Autor
Arda Dursun

---

**Hinweis**: Dies ist eine Demo-Anwendung. Für Produktionsumgebungen sollten zusätzliche Sicherheitsmaßnahmen und persistente Speicherung implementiert werden.
