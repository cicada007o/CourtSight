# BNS Legal Assistant - Troubleshooting Guide

Common issues and solutions for the BNS Legal Assistant system.

## Quick Diagnostics

### System Health Check
1. Visit `http://localhost:5000/health` to check system status
2. Check the application logs in `bns_legal_assistant.log`
3. Verify `.env` configuration file exists and is properly configured
4. Ensure PDF documents are in the `data` directory

### Common Quick Fixes
- **Restart the application**: Often resolves temporary issues
- **Check API key**: Ensure OpenAI API key is valid and has credit
- **Clear browser cache**: For frontend display issues
- **Reinitialize system**: Use the `/api/initialize` endpoint

---

## Installation Issues

### Python Version Error

**Error:**
```
Error: Python 3.7+ is required but not found
```

**Solution:**
1. Install Python 3.7+ from [python.org](https://python.org)
2. Ensure Python is in your system PATH
3. Use `python3` command on macOS/Linux

**Verification:**
```bash
python --version
# Should show Python 3.7.x or higher
```

### Virtual Environment Creation Failed

**Error:**
```
Failed to create virtual environment
```

**Solutions:**
```bash
# Install venv module (Ubuntu/Debian)
sudo apt install python3-venv

# Use alternative virtual environment tool
pip install virtualenv
virtualenv venv

# On Windows with Python from Microsoft Store
python -m venv venv --system-site-packages
```

### Dependency Installation Failed

**Error:**
```
Failed to install requirements
```

**Solutions:**
1. **Update pip first:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install with verbose output:**
   ```bash
   pip install -r requirements.txt -v
   ```

3. **Install dependencies individually:**
   ```bash
   pip install Flask==3.0.0
   pip install openai==1.3.7
   pip install chromadb==0.4.15
   # ... continue with other packages
   ```

4. **Use alternative package sources:**
   ```bash
   pip install -r requirements.txt -i https://pypi.org/simple
   ```

---

## Configuration Issues

### OpenAI API Key Problems

**Error:**
```
Error: OpenAI API key not configured
```

**Solution:**
1. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```env
   OPENAI_API_KEY=sk-your_actual_api_key_here
   ```

3. Verify key format (starts with `sk-`)

**Error:**
```
OpenAI API error: Incorrect API key provided
```

**Solutions:**
- Verify API key is copied correctly (no extra spaces)
- Check API key is active on OpenAI platform
- Ensure API key has available credit
- Try generating a new API key

### Environment File Issues

**Error:**
```
Configuration errors: OPENAI_API_KEY is not set
```

**Solutions:**
1. **Check file exists:**
   ```bash
   ls -la .env
   ```

2. **Verify file format:**
   ```env
   # Correct format (no spaces around =)
   OPENAI_API_KEY=sk-your_key_here
   
   # Incorrect format
   OPENAI_API_KEY = sk-your_key_here
   ```

3. **Check file permissions:**
   ```bash
   chmod 600 .env  # Unix/Linux/macOS
   ```

---

## PDF Processing Issues

### No PDF Files Found

**Error:**
```
No PDF documents found or processed
```

**Solutions:**
1. **Check data directory:**
   ```bash
   ls -la data/
   ```

2. **Add PDF files:**
   - Place BNS PDF files in `data/` directory
   - Ensure files have `.pdf` extension
   - Verify files are not corrupted

3. **Check file permissions:**
   ```bash
   chmod 644 data/*.pdf
   ```

### PDF Text Extraction Failed

**Error:**
```
Failed to extract text from PDF
```

**Solutions:**
1. **Verify PDF format:**
   - PDF must contain selectable text (not scanned images)
   - Try opening PDF in a text editor to verify text content

2. **Install additional dependencies:**
   ```bash
   # For better PDF processing
   pip install pdfplumber
   pip install pdfminer.six
   ```

3. **Try different PDF files:**
   - Use official BNS documents
   - Avoid password-protected PDFs
   - Convert scanned PDFs using OCR tools

---

## Vector Database Issues

### ChromaDB Initialization Failed

**Error:**
```
Failed to initialize ChromaDB
```

**Solutions:**
1. **Clear vector database:**
   ```bash
   rm -rf data/vector_db/
   mkdir -p data/vector_db/
   ```

2. **Check permissions:**
   ```bash
   chmod 755 data/
   chmod 755 data/vector_db/
   ```

3. **Install specific ChromaDB version:**
   ```bash
   pip install chromadb==0.4.15
   ```

### Embedding Generation Failed

**Error:**
```
Error generating embeddings
```

**Solutions:**
1. **Check OpenAI API status:**
   - Verify API key has embedding model access
   - Check OpenAI service status

2. **Try different embedding model:**
   ```env
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   ```

3. **Reduce chunk size:**
   ```env
   CHUNK_SIZE=400
   ```

---

## Runtime Issues

### Flask Application Won't Start

**Error:**
```
Address already in use
```

**Solutions:**
1. **Find and kill existing process:**
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /F /PID <process_id>
   
   # Unix/Linux/macOS
   lsof -ti:5000 | xargs kill -9
   ```

2. **Use different port:**
   ```python
   # In app.py
   app.run(port=5001)
   ```

### System Initialization Stuck

**Error:**
```
System initialization in progress (stuck)
```

**Solutions:**
1. **Restart application completely**

2. **Clear vector database:**
   ```bash
   rm -rf data/vector_db/
   ```

3. **Check logs for specific errors:**
   ```bash
   tail -f bns_legal_assistant.log
   ```

4. **Reinitialize via API:**
   ```bash
   curl -X POST http://localhost:5000/api/initialize
   ```

---

## Query Processing Issues

### Low Confidence Responses

**Issue:** AI responses have consistently low confidence scores

**Solutions:**
1. **Improve query phrasing:**
   - Be more specific
   - Use legal terminology
   - Reference BNS sections when known

2. **Adjust similarity threshold:**
   ```env
   SIMILARITY_THRESHOLD=0.5
   ```

3. **Increase retrieval documents:**
   ```env
   MAX_RETRIEVAL_DOCS=7
   ```

### No Relevant Documents Found

**Error:**
```
I couldn't find relevant information in the BNS documents
```

**Solutions:**
1. **Rephrase query:**
   - Use different keywords
   - Try more general terms
   - Ask about specific BNS sections

2. **Check PDF content:**
   - Verify PDFs contain expected legal content
   - Check if documents processed correctly

3. **Lower similarity threshold:**
   ```env
   SIMILARITY_THRESHOLD=0.3
   ```

---

## Performance Issues

### Slow Response Times

**Issue:** Queries take too long to process

**Solutions:**
1. **Check system resources:**
   ```bash
   # Monitor CPU and memory usage
   top  # Unix/Linux/macOS
   # Task Manager on Windows
   ```

2. **Optimize chunk settings:**
   ```env
   CHUNK_SIZE=600
   CHUNK_OVERLAP=50
   ```

3. **Use faster OpenAI model:**
   ```env
   OPENAI_MODEL=gpt-3.5-turbo
   ```

4. **Reduce retrieval documents:**
   ```env
   MAX_RETRIEVAL_DOCS=3
   ```

### Memory Issues

**Error:**
```
Out of memory errors
```

**Solutions:**
1. **Increase system memory**
2. **Process fewer documents at once**
3. **Use smaller chunk sizes:**
   ```env
   CHUNK_SIZE=400
   CHUNK_OVERLAP=25
   ```

---

## Browser/Frontend Issues

### Page Won't Load

**Issue:** Browser shows connection error

**Solutions:**
1. **Check Flask is running:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Try different browser**
3. **Clear browser cache and cookies**
4. **Check browser console for JavaScript errors**

### Chat Interface Not Working

**Issue:** Cannot send messages or responses not showing

**Solutions:**
1. **Check browser JavaScript console**
2. **Verify system status:**
   - Open browser dev tools (F12)
   - Check Network tab for API call failures

3. **Clear browser storage:**
   ```javascript
   // In browser console
   sessionStorage.clear();
   localStorage.clear();
   ```

---

## Network Issues

### API Connection Failed

**Error:**
```
Network error occurred
```

**Solutions:**
1. **Check internet connection**
2. **Verify OpenAI API accessibility:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **Check firewall settings**
4. **Try different DNS servers**

---

## Advanced Troubleshooting

### Enable Debug Mode

1. **Set environment variables:**
   ```env
   FLASK_DEBUG=True
   LOG_LEVEL=DEBUG
   ```

2. **Check detailed logs:**
   ```bash
   tail -f bns_legal_assistant.log
   ```

### Reset Everything

1. **Complete reset:**
   ```bash
   # Stop application
   # Remove virtual environment
   rm -rf venv/
   
   # Remove vector database
   rm -rf data/vector_db/
   
   # Remove logs
   rm -f bns_legal_assistant.log
   
   # Start fresh installation
   python setup.py
   ```

### Database Inspection

1. **Check vector database contents:**
   ```python
   import chromadb
   
   client = chromadb.PersistentClient(path="./data/vector_db")
   collection = client.get_collection("bns_legal_documents")
   print(f"Documents: {collection.count()}")
   ```

### Manual Testing

1. **Test individual components:**
   ```python
   # Test PDF processor
   from src.pdf_processor import BNSPDFProcessor
   processor = BNSPDFProcessor()
   chunks = processor.process_bns_documents()
   print(f"Processed {len(chunks)} chunks")
   
   # Test vector store
   from src.vector_store import BNSVectorStore
   store = BNSVectorStore()
   health = store.health_check()
   print(f"Vector store health: {health}")
   
   # Test RAG pipeline
   from src.rag_pipeline import BNSRAGPipeline
   rag = BNSRAGPipeline()
   response = rag.process_query("What is theft?")
   print(f"Response: {response}")
   ```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Review application logs**
3. **Try the system health check**
4. **Search for error messages online**

### Information to Provide

When reporting issues, include:
- Operating system and version
- Python version
- Error messages (full text)
- Application logs
- System status output
- Steps to reproduce the issue

### Log Locations

- **Application logs**: `bns_legal_assistant.log`
- **Flask logs**: Console output when running `python app.py`
- **Browser logs**: Browser developer console (F12)

---

## Prevention Tips

### Regular Maintenance

1. **Update dependencies periodically:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Monitor disk space** (vector database can grow large)

3. **Backup configuration:**
   ```bash
   cp .env .env.backup
   ```

4. **Monitor API usage and costs**

### Best Practices

1. **Use specific queries** for better results
2. **Keep PDF documents organized**
3. **Monitor system resources**
4. **Regular health checks**
5. **Keep OpenAI API key secure**

---

Still having issues? Check the main documentation or create an issue with detailed information about your problem.