# AI PDF FAQ Bot

Ein smarter Chatbot, der deine PDF-Dokumente versteht und Fragen dazu beantwortet. Perfekt für AGBs, Verträge, Rechnungen oder Lebensläufe - einfach PDF hochladen und losfragen.

## Was kann der Bot?

- **PDFs verstehen**: Lädt deine Dokumente hoch und extrahiert automatisch den Text
- **Intelligente Suche**: Findet die relevanten Stellen in deinen Dokumenten
- **Präzise Antworten**: Nutzt OpenAI GPT für natürliche, zusammenhängende Antworten (oder lokale Extraktion als Fallback)
- **Quellenangaben**: Zeigt dir immer an, aus welchem PDF und welcher Seite die Antwort stammt
- **Einfaches Login**: Registrierung und Login ohne komplizierte Setup-Schritte

## Schnellstart

### 1. Installation

```bash
# Repository klonen
git clone <repository-url>
cd "AI PDF FAQ Bot"

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### 2. OpenAI API Key einrichten (Optional, aber empfohlen)

Für die besten Ergebnisse solltest du einen OpenAI API Key verwenden. Ohne Key funktioniert die App auch, aber die Antworten sind dann weniger präzise.

```bash
# .env Datei erstellen
cp .env.example .env
```

Dann öffne die `.env` Datei und trage deinen API Key ein:

```env
OPENAI_API_KEY=sk-dein-api-key-hier
OPENAI_MODEL=gpt-3.5-turbo  # oder gpt-4 für noch bessere Ergebnisse
```

**Wo bekomme ich einen API Key?**  
Auf [platform.openai.com](https://platform.openai.com/api-keys) kannst du dir kostenlos einen erstellen. Die ersten $5 Guthaben sind gratis.

### 3. App starten

```bash
streamlit run app.py
```

Die App öffnet sich automatisch im Browser. Falls nicht, gehe zu `http://localhost:8501`

## So funktioniert's

1. **Account erstellen**: Beim ersten Start einfach einen neuen Account anlegen
2. **PDF hochladen**: Im Tab "PDFs hochladen" deine Dokumente auswählen und verarbeiten lassen
3. **Fragen stellen**: Im Tab "Fragen stellen" einfach deine Frage eingeben
4. **Antwort erhalten**: Der Bot sucht in deinen Dokumenten und gibt dir eine präzise Antwort mit Quellenangabe

### Beispiel-Fragen

- "Was ist meine Adresse?"
- "Wie lautet meine E-Mail-Adresse?"
- "Was steht in den AGBs zur Rückgabe?"
- "Welche Position habe ich in meinem Lebenslauf?"
- "Was sind die wichtigsten Punkte im Vertrag?"

## Technische Details

### Was wird verwendet?

- **Streamlit**: Für das Web-Interface
- **OpenAI GPT**: Für intelligente Antwortgenerierung (optional)
- **FAISS**: Für schnelle semantische Suche in den Dokumenten
- **Sentence Transformers**: Um Texte in Vektoren umzuwandeln
- **PyPDF2**: Zum Extrahieren von Text aus PDFs

### Wie funktioniert die Suche?

1. Dein PDF wird in kleine Textabschnitte (Chunks) aufgeteilt
2. Jeder Abschnitt wird in einen Vektor umgewandelt
3. Wenn du eine Frage stellst, wird auch diese in einen Vektor umgewandelt
4. Der Bot findet die ähnlichsten Abschnitte
5. Mit OpenAI wird daraus eine präzise Antwort generiert (oder lokal extrahiert)

### Konfiguration

In der `.env` Datei kannst du folgende Einstellungen vornehmen:

```env
# OpenAI (für bessere Antworten)
OPENAI_API_KEY=sk-dein-key
OPENAI_MODEL=gpt-3.5-turbo  # oder gpt-4

# Embedding Model (selten ändern nötig)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Projektstruktur

```
AI PDF FAQ Bot/
├── app.py                 # Hauptanwendung (Streamlit)
├── config.py             # Konfiguration
├── database_dummy.py     # In-Memory Datenbank
├── models/
│   ├── pdf_processor.py  # PDF-Verarbeitung
│   └── embeddings.py     # Embeddings & FAISS
├── services/
│   ├── qa_service.py     # Q&A Logik
│   └── user_service.py   # User Management
└── requirements.txt      # Python Packages
```

## Wichtige Hinweise

- **Keine Datenbank nötig**: Alles läuft im Speicher. Beim Neustart gehen die Daten verloren, aber die FAISS-Indizes bleiben erhalten
- **Kosten**: Mit OpenAI API Key fallen Kosten an (ca. $0.002 pro Frage mit GPT-3.5-turbo). Ohne API Key ist es kostenlos, aber weniger präzise
- **Offline-Modus**: Die App funktioniert auch komplett offline (nach dem ersten Download der Modelle), wenn kein OpenAI Key verwendet wird

## Häufige Probleme

**App startet nicht?**
- Prüfe, ob Python 3.10+ installiert ist: `python3 --version`
- Stelle sicher, dass alle Dependencies installiert sind: `pip install -r requirements.txt`

**PDF wird nicht verarbeitet?**
- Das PDF muss Text enthalten (nicht nur Bilder)
- Prüfe die Fehlermeldungen in der App

**Keine Antworten?**
- Stelle sicher, dass PDFs hochgeladen wurden
- Formuliere deine Fragen präziser
- Prüfe, ob die Information wirklich im Dokument steht

**OpenAI Fehler?**
- Prüfe, ob dein API Key korrekt in der `.env` Datei steht
- Stelle sicher, dass du noch Guthaben auf deinem OpenAI Account hast
- Die App fällt automatisch auf die lokale Methode zurück, falls OpenAI nicht verfügbar ist

## Lizenz

Dieses Projekt ist frei verfügbar für persönliche und kommerzielle Nutzung.

## Credits

- HuggingFace für Sentence Transformers
- Meta AI für FAISS
- Streamlit für das Framework
- OpenAI für die GPT-Modelle

---

**Tipp**: Für den besten Start empfehle ich, einen OpenAI API Key zu verwenden. Die Antwortqualität ist damit deutlich besser und die Kosten sind minimal (ca. 2 Cent pro 1000 Fragen mit GPT-3.5-turbo).
