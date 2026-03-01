# FinanceDepictor

A personal finance dashboard for uploading, parsing, and analyzing bank statements with automatic categorization and spending insights.

## Overview
FinanceDepictor is a **Streamlit-based** web application that extracts transactions from PDF and OFX bank statements, stores them in SQLite, and provides interactive visualizations of your spending patterns over time.

## Features
- 🔐 **User Authentication**: Secure signup/login with PBKDF2 password hashing
- 📄 **Multi-Format Support**: Upload PDF (FNB, Discovery Bank) and OFX/QFX statements
- 🏦 **Auto Bank Detection**: Automatically identifies bank from statement headers
- 💾 **SQLite Storage**: Persistent transaction storage with deduplication
- 📊 **Interactive Dashboards**: Monthly and yearly spending analysis with Plotly charts
- 🏷️ **Smart Categorization**: Rule-based transaction categorization with keyword matching
- ⚡ **Streamlit Caching**: Fast data loading with `@st.cache_resource` for DB connections

## Project Structure
```
FinanceDepictor/
├── streamlit_app.py              # Main entrypoint
├── app_ui/                       # UI components
│   ├── auth.py                   # Authentication & session management
│   ├── data.py                   # Data loading with caching
│   └── pages/                    # Page modules (dashboard, upload, analysis)
├── scripts/
│   ├── PDF_Stuff.py              # PDF parsing (FNBReadPDF, DiscoveryReadPDF)
│   ├── ofx_reader.py             # OFX/QFX file parsing
│   ├── bank_detector.py          # Auto-detect bank from file headers
│   ├── db_manager.py             # Database operations with Streamlit caching
│   ├── db_schema.py              # SQLAlchemy models (User, Transaction, etc.)
│   ├── category_functions.py    # Category matching logic
│   └── categories_manager.py    # Category CRUD operations
├── migrations/
│   └── 001_create_schema.sql     # Database schema
├── finance.db                    # SQLite database (auto-created)
└── PROJECT_CONTEXT.md            # Detailed technical documentation

```

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd FinanceDepictor

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- streamlit
- sqlalchemy
- pdfplumber
- ofxparse
- plotly
- pandas
- numpy

## Usage

### Running the Application
```bash
# Activate virtual environment first (see above)
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### First Time Setup
1. **Create Account**: Click "Sign Up" and create a new user account
2. **Upload Statements**: Go to "Upload Bank Statements" page
3. **Select Files**: Upload PDF or OFX files (supports multiple files)
4. **Auto-Detection**: The app will detect your bank automatically or you can select manually
5. **View Transactions**: Preview extracted transactions before adding to dataset
6. **Analyze**: Navigate to Dashboard, Monthly, or Year Analysis pages

### Supported Banks
- **FNB** (First National Bank) - PDF statements
- **Discovery Bank** - PDF statements
- **OFX/QFX** - Any bank supporting OFX export format

## Architecture

### Database Schema
- **users**: User accounts with hashed passwords
- **accounts**: Bank accounts linked to users
- **files**: Uploaded statement metadata
- **transactions**: Parsed transaction records
- **categories**: Spending categories (hierarchical)
- **rules**: Auto-categorization rules

### Data Flow
1. User uploads statement file
2. Bank detection runs on file headers
3. Check DB for duplicate (by filename)
4. Parse file if new (FNBReadPDF/DiscoveryReadPDF/OFX)
5. Store transactions + file metadata in SQLite
6. Display preview and insights

### Caching Strategy
- **DB Connections**: `@st.cache_resource` on SQLAlchemy engine (persistent across reruns)
- **Data Loaders**: `@st.cache_data` for categories, category functions
- **Deduplication**: Check `file_already_parsed()` before re-parsing files

## Development

### Branch Strategy
- `main`: Stable Flask version (preserved for demos/portfolio)
- `streamlit-implementation`: Active Streamlit development (current)

### Running Tests
```bash
# TODO: Add test suite
pytest tests/
```

### VS Code Debugging
Use the included `.vscode/launch.json` configuration to debug the Streamlit app.

## Recent Updates
- ✅ Migrated from Flask to Streamlit
- ✅ Replaced `PDFContentConverter` with `pdfplumber`
- ✅ Added OFX/QFX support via `ofxparse`
- ✅ Implemented bank auto-detection
- ✅ Replaced JSON cache with SQLite + Streamlit caching
- ✅ Added user authentication with secure password hashing
- ✅ Modularized codebase into `app_ui` package

## TODOs
- [ ] Implement "Add to dataset" persistence logic
- [ ] Add category auto-matching on upload
- [ ] Build category editing UI
- [ ] Add account selection (currently hard-coded)
- [ ] Write unit tests for core modules
- [ ] Add SQLite indices for performance
- [ ] Implement data export (CSV/JSON)
- [ ] Multi-user support (pull user ID from session)
- [ ] Add more bank parsers
- [ ] Containerize with Docker

## Contributing
This is a personal project, but suggestions and improvements are welcome!

## License
[Add license information]

## Contact
[Add contact information]

---

For detailed technical documentation, see [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).
