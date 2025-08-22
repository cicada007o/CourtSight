"""
BNS Legal Assistant - Main Flask Application
Production-ready Flask app for legal consultation based on BNS 2023.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
import uuid
from src.config import Config
from src.pdf_processor import BNSPDFProcessor
from src.vector_store import BNSVectorStore
from src.rag_pipeline import BNSRAGPipeline

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bns_legal_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Global variables for system components
rag_pipeline = None
system_initialized = False
initialization_status = {"status": "not_started", "message": "System not initialized"}

def initialize_system():
    """Initialize the BNS Legal Assistant system components."""
    global rag_pipeline, system_initialized, initialization_status
    
    try:
        initialization_status = {"status": "in_progress", "message": "Initializing system components..."}
        logger.info("Starting system initialization")
        
        # Validate configuration
        config_valid, config_errors = Config.validate_config()
        if not config_valid:
            raise Exception(f"Configuration errors: {'; '.join(config_errors)}")
        
        initialization_status["message"] = "Configuration validated. Initializing RAG pipeline..."
        
        # Initialize RAG pipeline
        rag_pipeline = BNSRAGPipeline()
        
        initialization_status["message"] = "Checking system health..."
        
        # Check system health
        system_status = rag_pipeline.get_system_status()
        
        if system_status.get('ready_for_queries'):
            system_initialized = True
            initialization_status = {
                "status": "completed",
                "message": "System initialized successfully and ready for queries",
                "document_count": system_status.get('collection_stats', {}).get('total_documents', 0)
            }
            logger.info("System initialization completed successfully")
        else:
            # Try to process PDFs if collection is empty
            collection_stats = system_status.get('collection_stats', {})
            if collection_stats.get('total_documents', 0) == 0:
                initialization_status["message"] = "No documents found. Processing BNS PDFs..."
                process_result = process_bns_documents()
                
                if process_result.get('success'):
                    system_initialized = True
                    initialization_status = {
                        "status": "completed",
                        "message": "System initialized with processed documents",
                        "document_count": process_result.get('chunks_created', 0)
                    }
                    logger.info("System initialization completed with document processing")
                else:
                    initialization_status = {
                        "status": "error",
                        "message": f"Failed to process documents: {process_result.get('error', 'Unknown error')}"
                    }
            else:
                system_initialized = True
                initialization_status = {
                    "status": "completed",
                    "message": "System initialized with existing documents",
                    "document_count": collection_stats.get('total_documents', 0)
                }
                logger.info("System initialization completed with existing documents")
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        initialization_status = {
            "status": "error",
            "message": f"Initialization failed: {str(e)}"
        }

def process_bns_documents():
    """Process BNS PDF documents and add them to the vector store."""
    try:
        logger.info("Starting BNS document processing")
        
        # Initialize components
        pdf_processor = BNSPDFProcessor()
        vector_store = BNSVectorStore()
        
        # Process PDFs
        chunks = pdf_processor.process_bns_documents()
        
        if not chunks:
            return {
                "success": False,
                "error": "No PDF documents found or processed. Please add BNS PDF files to the data directory.",
                "chunks_created": 0
            }
        
        # Add chunks to vector store
        success = vector_store.add_chunks(chunks)
        
        if success:
            stats = pdf_processor.get_processing_stats(chunks)
            logger.info(f"Document processing completed. Created {len(chunks)} chunks")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "processing_stats": stats
            }
        else:
            return {
                "success": False,
                "error": "Failed to add processed chunks to vector store",
                "chunks_created": 0
            }
            
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "chunks_created": 0
        }

# Flask Routes

@app.route('/')
def index():
    """Landing page with system overview."""
    return render_template('index.html', 
                         system_ready=system_initialized,
                         initialization_status=initialization_status)

@app.route('/chat')
def chat():
    """Interactive chat interface."""
    if not session.get('session_id'):
        session['session_id'] = str(uuid.uuid4())
        session['questions_asked'] = 0
        session['session_start'] = datetime.now().isoformat()
    
    # Get example queries
    example_queries = []
    if rag_pipeline:
        example_queries = rag_pipeline.get_example_queries()
    
    return render_template('chat.html',
                         system_ready=system_initialized,
                         initialization_status=initialization_status,
                         example_queries=example_queries,
                         session_id=session['session_id'])

@app.route('/api/ask', methods=['POST'])
def api_ask():
    """API endpoint for legal questions."""
    try:
        if not system_initialized or not rag_pipeline:
            return jsonify({
                'success': False,
                'error': 'System not initialized. Please wait for initialization to complete.',
                'initialization_status': initialization_status
            }), 503
        
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'No query provided. Please include "query" in the JSON request body.'
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Empty query provided. Please ask a specific legal question.'
            }), 400
        
        # Update session stats
        if not session.get('session_id'):
            session['session_id'] = str(uuid.uuid4())
            session['questions_asked'] = 0
            session['session_start'] = datetime.now().isoformat()
        
        session['questions_asked'] = session.get('questions_asked', 0) + 1
        
        # Process query through RAG pipeline
        logger.info(f"Processing query from session {session['session_id']}: {query[:100]}...")
        response = rag_pipeline.process_query(query)
        
        # Add session information
        response['session_id'] = session['session_id']
        response['question_number'] = session['questions_asked']
        response['timestamp'] = datetime.now().isoformat()
        
        # Log query and response
        logger.info(f"Query processed. Success: {response['success']}, Confidence: {response.get('confidence', 0):.2f}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing API request: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error. Please try again later.',
            'details': str(e) if Config.FLASK_DEBUG else None
        }), 500

@app.route('/api/status')
def api_status():
    """API endpoint for system status."""
    try:
        if not rag_pipeline:
            return jsonify({
                'overall_status': 'initializing',
                'initialization_status': initialization_status,
                'ready_for_queries': False,
                'system_info': {
                    'config': Config.get_summary(),
                    'timestamp': datetime.now().isoformat()
                }
            })
        
        # Get comprehensive system status
        system_status = rag_pipeline.get_system_status()
        system_status['initialization_status'] = initialization_status
        system_status['timestamp'] = datetime.now().isoformat()
        
        return jsonify(system_status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'ready_for_queries': False,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    """API endpoint to reinitialize the system."""
    try:
        global system_initialized
        system_initialized = False
        
        # Run initialization in background (for production, use Celery or similar)
        initialize_system()
        
        return jsonify({
            'success': True,
            'message': 'System reinitialization started',
            'status': initialization_status
        })
        
    except Exception as e:
        logger.error(f"Error reinitializing system: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/examples')
def api_examples():
    """API endpoint for example queries."""
    try:
        if not rag_pipeline:
            return jsonify({
                'success': False,
                'error': 'System not initialized',
                'examples': []
            })
        
        examples = rag_pipeline.get_example_queries()
        return jsonify({
            'success': True,
            'examples': examples
        })
        
    except Exception as e:
        logger.error(f"Error getting examples: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'examples': []
        })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        health_status = {
            'status': 'healthy' if system_initialized else 'initializing',
            'timestamp': datetime.now().isoformat(),
            'initialization_status': initialization_status,
            'config_valid': Config.validate_config()[0]
        }
        
        if rag_pipeline:
            system_status = rag_pipeline.get_system_status()
            health_status.update(system_status)
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'API endpoint not found',
            'available_endpoints': ['/api/ask', '/api/status', '/api/initialize', '/api/examples']
        }), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'timestamp': datetime.now().isoformat()
        }), 500
    return render_template('index.html'), 500

# Initialize system on startup
@app.before_first_request
def startup():
    """Initialize system components on first request."""
    if not system_initialized:
        logger.info("Starting BNS Legal Assistant application")
        initialize_system()

if __name__ == '__main__':
    logger.info("Starting BNS Legal Assistant Flask application")
    
    # Initialize system
    initialize_system()
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_DEBUG,
        threaded=True
    )