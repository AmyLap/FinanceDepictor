# FinanceDepictor Project Context

## Project Overview
**FinanceDepictor** is a personal finance dashboard and statement management tool. It allows users to:
- Upload bank statements (PDF, OFX) from multiple banks
- Automatically extract transactions
- Categorize spending by category
- Analyze spending patterns over time (monthly, yearly views)
- Track and audit transaction categorization

## Architecture

### Technology Stack
- **UI Framework**: Streamlit (interactive web dashboard)
- **Backend**: Python 3.14.2
- **Database**: SQLite (`finance.db`) with SQLAlchemy ORM
- **PDF Parsing**: `pdfplumber` (replaced untrusted `PDFContentConverter`)
- **OFX Parsing**: `ofxparse`
- **Data Processing**: pandas, numpy
- **Plotting**: plotly (px and graph_objects)
- **Caching**: Streamlit's `@st.cache_resource` for DB connections
- **Authentication**: Local signup/login with PBKDF2-HMAC-SHA256 password hashing

### Directory Structure
```
FinanceDepictor/
├── streamlit_app.py              # Entrypoint (minimal, delegates to app_ui)
├── app_ui/                       # Modularized Streamlit components
│   ├── __init__.py
│   ├── auth.py                   # Auth management, session guard
│   ├── data.py                   # AppData dataclass, cached data loaders
│   └── pages/
│       ├── __init__.py           # PAGE_NAMES, PAGE_RENDERERS
│       ├── dashboard.py          # Metrics and category overview
│       ├── upload_statements.py  # File upload, bank detection, parsing
│       ├── monthly_analysis.py   # Monthly spending breakdown
│       ├── categories.py         # Category management UI
│       └── year_analysis.py      # Yearly spending trends
├── scripts/
│   ├── PDF_Stuff.py              # ReadPDF base class, FNBReadPDF, DiscoveryReadPDF
│   ├── ofx_reader.py             # OFX/QFX file parsing
│   ├── bank_detector.py          # Auto-detect bank from PDF/OFX headers
│   ├── db_manager.py             # DB operations with Streamlit caching
│   ├── db_schema.py              # SQLAlchemy models (User, Account, Transaction, etc.)
│   ├── category_functions.py     # Category matching and rules
│   ├── categories_manager.py     # Category CRUD operations
│   ├── utils.py                  # Utility methods (date validation, etc.)
│   └── cache.py                  # [DEPRECATED] JSON cache (replaced by db_manager.py)
├── static/
│   ├── bootstrap.css
│   ├── categories.js
│   └── monthly_graphs.js
├── templates/                    # [LEGACY] Flask templates (preserved on main branch)
├── migrations/
│   └── 001_create_schema.sql     # Initial database schema
├── logs/
│   ├── cache.json                # [DEPRECATED] JSON file cache
│   ├── cache_copy.json
│   ├── categories.json
│   └── categorised.json
└── README.md
```

### Version Control
- **Current Branch**: `streamlit-implementation` (active development)
- **Main Branch**: Preserved Flask app (for hiring/demo)
- **DB File**: `finance.db` (SQLite, created at project root)

## Database Schema

### Key Tables
1. **users** — User accounts with salted PBKDF2 passwords
2. **accounts** — Bank accounts linked to users
3. **files** — Metadata for uploaded statement files
4. **transactions** — Parsed transaction records (Year, Month, Date, Type, Details, Amount)
5. **categories** — Spending categories (hierarchical)
6. **rules** — Auto-categorization rules (pattern → category)
7. **transaction_category_history** — Audit trail for category changes

### Transaction Fields
- `file_id`: Links to uploaded file
- `account_id`: Associated account
- `date`: Transaction date
- `amount`: Transaction amount (numeric)
- `merchant`: Type/merchant name
- `description`: Transaction details
- `category_id`: Assigned category (if categorized)

## Data Flow

### Upload & Parsing Pipeline
1. **User uploads** PDF/OFX file via `upload_statements.py`
2. **Bank detection** via `scripts/bank_detector.py`:
   - Reads first page of PDF and searches for keywords (FNB, Discovery)
   - Reads OFX headers for ORG tags
   - Returns `'fnb'`, `'discovery'`, or `'unknown'`
3. **DB check** via `file_already_parsed()`:
   - If file was previously uploaded, retrieve cached transactions from DB
   - Skip parsing step
4. **Parsing** (if new):
   - **PDF**: Route to `FNBReadPDF` or `DiscoveryReadPDF` (child classes of `ReadPDF`)
   - **OFX**: Route to `read_ofx_to_df()` from `ofx_reader.py`
   - Produces DataFrame: `[Year, Month, Date, Type, Details, Amount]`
5. **Storage** via `write_transactions()`:
   - Insert `FileMeta` record with filename, file_type, upload_at
   - Insert `Transaction` rows into DB
   - Idempotent: skips if file already exists
6. **Display**:
   - Show extracted transactions in a preview table
   - Button: "Add to dataset" (currently placeholder)

### Authentication Flow
1. User navigates to app → `guard_authenticated()` in `auth.py`
2. If no active session → render login/signup page
3. Signup: salt password, hash with PBKDF2, store in `users` table
4. Login: retrieve user, verify password, set `st.session_state['user']`
5. Authenticated: display sidebar with username and pages

### Data Caching Strategy (Streamlit)
- **DB Connection**: `@st.cache_resource` decorator in `get_db()` ensures one persistent SQLAlchemy engine per session
  - Engine and session factory cached across Streamlit reruns
  - No repeated connection initialization
- **App Data**: `@st.cache_data` in `app_ui/data.py` for load_data(), get_category_functions(), etc.
- **JSON Cache (legacy)**: `logs/cache.json` — **deprecated**, replaced by DB

## Key Modules

### `scripts/PDF_Stuff.py`
- **ReadPDF** (base class)
  - `read_pdf_coords_and_sort()`: Extract words with coordinates via pdfplumber, group into lines
  - `document_to_df()`: Orchestrate parsing, detect bank, call appropriate subclass method
  - `get_year()`, `get_month()`: Extract statement date from line data
- **FNBReadPDF** (subclass)
  - `fnb_to_df()`: Parse FNB statement format (4–5 columns per transaction)
- **DiscoveryReadPDF** (subclass)
  - `discovery_table_to_df()`: Parse Discovery statement format (4–5 columns, handle "Inter account" edge case)
- **Note**: No longer handles caching; `ReadPDF.cache_data()` raises `NotImplementedError`

### `scripts/ofx_reader.py`
- `read_ofx_to_df(file_path)`: Parse OFX/QFX files using `ofxparse`
  - Returns DataFrame with columns: `[Year, Month, Date, Type, Details, Amount]`
  - Extracts debits only by default (user can modify)

### `scripts/bank_detector.py`
- `detect_pdf_bank(file_path) -> str`: Scan first page text for bank keywords
- `detect_ofx_bank(file_path) -> str`: Search OFX headers (`<ORG>` tag, etc.)
- `detect_bank(file_path) -> str`: Dispatcher by file extension
- **Mapping**: `_BANK_KEYWORDS` dict; easy to extend with new banks

### `scripts/db_manager.py`
- `get_db(db_url)`: Cached SQLAlchemy engine + session factory (`@st.cache_resource`)
- `file_already_parsed(filename, user_id)`: Boolean check
- `get_file_transactions(filename, user_id)`: Retrieve cached rows as list-of-lists
- `write_transactions(transactions, filename, bank, account_id, user_id)`: Insert into DB (idempotent)

### `app_ui/auth.py`
- `initialize_auth_db()`: Create users table if missing
- `hash_password()`, `create_user()`: Password handling
- `authenticate_user()`: Login logic
- `guard_authenticated()`: Session guard (renders login if unauthenticated)
- `render_user_sidebar()`: Username + logout button

### `app_ui/data.py`
- `AppData` dataclass: Holds loaded categories, functions, etc.
- `get_app_data()`: Cached loader that instantiates `CategoryFunctions`, `CategoriesManager`
- `load_data()`, `get_category_functions()`, `get_categories_manager()`: Individual cached loaders

### `app_ui/pages/upload_statements.py`
- Render file uploader
- Detect bank, check DB, parse if needed, write to DB
- Display preview and "Add to dataset" button

## Recent Changes (Session History)

### Phase 1: Streamlit Scaffold
- Created `streamlit_app.py` entrypoint
- Modularized code into `app_ui` package (auth, data, pages)

### Phase 2: Authentication
- Implemented signup/login with PBKDF2 password hashing
- Session state guard to protect pages

### Phase 3: PDF & OFX Integration
- Replaced `PDFContentConverter` with `pdfplumber` in `PDF_Stuff.py`
- Added `ofx_reader.py` for OFX parsing
- Created `FNBReadPDF`, `DiscoveryReadPDF` subclasses

### Phase 4: Bank Detection
- Created `bank_detector.py` with keyword-based detection
- Added manual bank selector in upload UI
- Fallback logic: try Discovery, then FNB on unknown

### Phase 5: Cache Removal & DB Integration
- **Removed**: JSON-based `scripts/cache.py` (was for data storage, not speed)
- **Added**: `scripts/db_manager.py` with Streamlit `@st.cache_resource`
- **Updated**: `upload_statements.py` to:
  - Query DB for previously parsed files
  - Write parsed transactions to SQLite
  - Show "Loaded from database" message on cache hit
- **Benefit**: Persistent, queryable data store; leverages Streamlit's connection caching

## Current Known Limitations & TODO

### Upload Flow
- "Add to dataset" button is a placeholder (no persistence logic yet)
- Account selection is hard-coded to `account_id=1` in `write_transactions()`
- User ID hard-coded to `user_id=1` (not pulling from session)

### Database
- No migration system yet (SQLAlchemy creates tables on first run)
- No indices on `transactions` for performance tuning
- No soft deletes (e.g., for file removal)

### Parsing
- PDF parsing assumes specific bank formats; may fail on new statement layouts
- OFX parsing extracts debits only (can add credits if needed)
- No error recovery / partial transaction insertion on parse failure

### Testing
- No unit tests for `bank_detector`, `db_manager`, `ofx_reader`
- No integration tests for upload flow end-to-end

## Development Notes

### Running the App
```bash
# In PowerShell, from project root:
.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

### Python Environment
- **Type**: virtualenv
- **Location**: `.venv/`
- **Version**: Python 3.14.2
- **Key Packages**: streamlit, sqlalchemy, pdfplumber, ofxparse, plotly, pandas

### Database Location
- **File**: `finance.db` (created at project root when app first runs)
- **Initialization**: Automatic via `Base.metadata.create_all(engine)` in `db_manager.py`

### Debugging
- Set `.vscode/launch.json` to launch `streamlit run streamlit_app.py` as a module
- Session state and errors logged to browser console

## Next Steps (Suggested)
1. Implement "Add to dataset" logic (merge transactions into a canonical dataset)
2. Add category auto-matching via `CategoryFunctions`
3. Implement category editing/audit trail UI
4. Add account selection UI (not hard-coded)
5. Write unit tests for core modules
6. Add SQLite indices for transaction queries
7. Implement data export (CSV, JSON)
8. Add multi-user support (pull user ID from session)
