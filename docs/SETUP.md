# BNS Legal Assistant - Setup Guide

Complete setup instructions for the BNS Legal Assistant - an AI-powered legal consultation system based on the Bharatiya Nyaya Sanhita (BNS) 2023.

## Prerequisites

### Required Software
- **Python 3.7+** - Download from [python.org](https://python.org)
- **Git** (optional) - For cloning the repository
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space for dependencies and vector database
- **Internet**: Required for OpenAI API calls and initial setup

## Quick Start (Windows)

### Option 1: One-Click Installation
1. Download or clone the project
2. Double-click `install.bat`
3. Follow the on-screen instructions
4. Edit `.env` file with your OpenAI API key
5. Place BNS PDF files in the `data` folder
6. Double-click `run.bat` to start

### Option 2: Manual Installation
```cmd
# Clone the repository
git clone <repository-url>
cd bns-legal-assistant

# Run automated setup
python setup.py

# Configure environment
copy .env.example .env
# Edit .env and add your OpenAI API key

# Start the application
run.bat
```

## Manual Setup (All Platforms)

### Step 1: Environment Setup

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configuration

#### Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

#### Required Configuration
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

### Step 3: Document Preparation

#### Add BNS PDF Files
1. Create `data` directory if it doesn't exist
2. Place BNS PDF documents in the `data` folder
3. Supported formats: PDF files with text content
4. Recommended: Official BNS 2023 documents

#### Directory Structure
```
data/
├── bns-2023-main.pdf
├── bns-2023-appendix.pdf
└── other-legal-documents.pdf
```

### Step 4: First Run

#### Start the Application
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Start the server
python app.py
```

#### Initialize System
1. Open browser to `http://localhost:5000`
2. System will automatically process PDF documents on first run
3. Wait for initialization to complete
4. Start using the legal consultation chat

## Platform-Specific Instructions

### Windows Setup

#### Prerequisites
```cmd
# Check Python installation
python --version
# Should show Python 3.7 or higher

# Install/upgrade pip
python -m pip install --upgrade pip
```

#### Using PowerShell
```powershell
# Set execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### macOS Setup

#### Prerequisites
```bash
# Install Python via Homebrew (recommended)
brew install python

# Or use system Python
python3 --version
```

#### Setup Process
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make run script executable
chmod +x run.sh
```

### Linux (Ubuntu/Debian) Setup

#### Prerequisites
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install system dependencies
sudo apt install build-essential
```

#### Setup Process
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start application
python app.py
```

## Configuration Options

### Environment Variables

#### OpenAI Settings
```env
OPENAI_API_KEY=sk-...                    # Required: Your OpenAI API key
OPENAI_MODEL=gpt-3.5-turbo              # GPT model for responses
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002  # Embedding model
```

#### Flask Settings
```env
FLASK_ENV=development                    # Environment (development/production)
FLASK_DEBUG=True                        # Debug mode
SECRET_KEY=your_secret_key_here         # Session encryption key
```

#### Vector Store Settings
```env
VECTOR_DB_PATH=./data/vector_db         # ChromaDB storage path
COLLECTION_NAME=bns_legal_documents     # Collection name
```

#### Processing Settings
```env
PDF_DATA_PATH=./data                    # PDF files directory
CHUNK_SIZE=800                          # Text chunk size
CHUNK_OVERLAP=100                       # Chunk overlap size
MAX_RETRIEVAL_DOCS=5                    # Max documents per query
SIMILARITY_THRESHOLD=0.7                # Similarity cutoff
```

### Advanced Configuration

#### Custom PDF Processing
```python
# Modify src/pdf_processor.py
CHUNK_SIZE = 1000  # Larger chunks for more context
CHUNK_OVERLAP = 150  # More overlap for better continuity
```

#### Model Selection
```env
# Use GPT-4 (requires API access)
OPENAI_MODEL=gpt-4

# Use different embedding model
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

## Verification

### Test Installation
```bash
# Check if all dependencies are installed
pip list

# Test Python imports
python -c "import openai, chromadb, PyPDF2; print('All imports successful')"

# Check environment variables
python -c "import os; print('OpenAI key configured:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Test Application
1. Start the application: `python app.py`
2. Open browser to `http://localhost:5000`
3. Check system status in the interface
4. Try asking a test question
5. Verify PDF processing in logs

### Health Check Endpoint
```bash
# Check system health via API
curl http://localhost:5000/health

# Check system status
curl http://localhost:5000/api/status
```

## Troubleshooting

### Common Issues

#### Python Version Error
```
Error: Python 3.7+ is required
```
**Solution**: Install Python 3.7 or higher from [python.org](https://python.org)

#### OpenAI API Error
```
Error: OpenAI API key not configured
```
**Solution**: Add valid API key to `.env` file

#### PDF Processing Failed
```
Error: No PDF documents found
```
**Solution**: Place PDF files in the `data` directory

#### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port in `app.py` or kill existing process

### Getting Help

#### Log Files
- Application logs: `bns_legal_assistant.log`
- System console output for detailed error messages

#### Debug Mode
```env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

#### Support Resources
- Check `docs/TROUBLESHOOTING.md` for detailed solutions
- Review application logs for specific error messages
- Ensure all prerequisites are properly installed

## Production Deployment

### Security Considerations
```env
# Production settings
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=generate_secure_random_key_here
```

### Performance Optimization
- Use production WSGI server (gunicorn, uWSGI)
- Configure reverse proxy (nginx)
- Set up SSL/HTTPS
- Monitor system resources
- Implement rate limiting

### Example Production Config
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

---

## Next Steps

After successful setup:
1. Read `docs/API.md` for API documentation
2. Check `docs/TROUBLESHOOTING.md` for common issues
3. Review the main `README.md` for usage instructions
4. Start exploring BNS legal consultations!