"""
Simple Flask app to demonstrate the BNS Legal Assistant structure
without heavy dependencies for testing purposes.
"""

from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'demo-secret-key-for-testing'

# Mock data for demonstration
MOCK_RESPONSES = {
    "theft": {
        "answer": "According to the Bharatiya Nyaya Sanhita (BNS) 2023, theft is defined in Section 303. Whoever intends dishonestly to take any movable property out of the possession of any person without that person's consent, is said to commit theft. The punishment for theft under Section 303 includes imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "confidence": 0.92,
        "sections_cited": ["Section 303"],
        "query_type": "definition",
        "retrieved_docs": 2
    },
    "assault": {
        "answer": "Under the Bharatiya Nyaya Sanhita (BNS) 2023, assault is covered under Section 321. Simple assault is punishable with imprisonment of either description for a term which may extend to three months, or with fine which may extend to five hundred rupees, or with both. For voluntary causing of hurt, the punishment is imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both.",
        "confidence": 0.88,
        "sections_cited": ["Section 321", "Section 322"],
        "query_type": "penalty",
        "retrieved_docs": 3
    }
}

# Mock system status
SYSTEM_STATUS = {
    "overall_status": "healthy",
    "ready_for_queries": True,
    "initialization_status": {
        "status": "completed",
        "message": "Demo system ready - mock responses enabled",
        "document_count": 1000
    },
    "collection_stats": {
        "total_documents": 1000,
        "content_types": {
            "definition": 245,
            "penalty": 189,
            "procedure": 156,
            "general": 410
        },
        "sources": ["bns-2023-demo.pdf"],
        "collection_name": "bns_legal_documents_demo"
    }
}

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html', 
                         system_ready=True,
                         initialization_status=SYSTEM_STATUS['initialization_status'])

@app.route('/chat')
def chat():
    """Chat interface."""
    example_queries = [
        {
            'category': 'Definitions',
            'query': 'What is the definition of theft under BNS?',
            'description': 'Get clear definitions of legal terms and concepts'
        },
        {
            'category': 'Penalties',
            'query': 'What is the punishment for assault under BNS?',
            'description': 'Learn about specific penalties and punishments'
        },
        {
            'category': 'Procedures',
            'query': 'What is the procedure for filing a complaint?',
            'description': 'Understand legal processes and procedures'
        }
    ]
    
    return render_template('chat.html',
                         system_ready=True,
                         initialization_status=SYSTEM_STATUS['initialization_status'],
                         example_queries=example_queries,
                         session_id='demo-session-123')

@app.route('/api/ask', methods=['POST'])
def api_ask():
    """API endpoint for legal questions - demo version."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'No query provided. Please include "query" in the JSON request body.'
            }), 400
        
        query = data['query'].strip().lower()
        
        # Mock response based on query content
        if 'theft' in query:
            response = MOCK_RESPONSES['theft'].copy()
        elif 'assault' in query or 'hurt' in query:
            response = MOCK_RESPONSES['assault'].copy()
        else:
            response = {
                "answer": "This is a demonstration response. In the full system, this query would be processed through the RAG pipeline using actual BNS documents to provide accurate legal information. The query would be enhanced, relevant documents retrieved, and a comprehensive response generated with proper citations.",
                "confidence": 0.75,
                "sections_cited": ["Demo Section"],
                "query_type": "general",
                "retrieved_docs": 1
            }
        
        # Add demo metadata
        response.update({
            'success': True,
            'session_id': 'demo-session-123',
            'question_number': 1,
            'timestamp': datetime.now().isoformat(),
            'model_used': 'demo-gpt-3.5-turbo',
            'source_documents': [
                {
                    'text': 'This is a sample excerpt from a BNS document that would be retrieved...',
                    'section': 'Demo Section',
                    'content_type': response['query_type'],
                    'relevance_score': response['confidence']
                }
            ]
        })
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Demo error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status')
def api_status():
    """API endpoint for system status - demo version."""
    status = SYSTEM_STATUS.copy()
    status['timestamp'] = datetime.now().isoformat()
    return jsonify(status)

@app.route('/api/examples')
def api_examples():
    """API endpoint for example queries."""
    examples = [
        {
            'category': 'Definitions',
            'query': 'What is the definition of theft under BNS?',
            'description': 'Get clear definitions of legal terms and concepts'
        },
        {
            'category': 'Penalties',
            'query': 'What is the punishment for assault under BNS?',
            'description': 'Learn about specific penalties and punishments'
        },
        {
            'category': 'Procedures',
            'query': 'What is the procedure for filing a complaint?',
            'description': 'Understand legal processes and procedures'
        },
        {
            'category': 'Offences',
            'query': 'What constitutes a criminal breach of trust?',
            'description': 'Learn about different types of criminal offences'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'initialization_status': SYSTEM_STATUS['initialization_status'],
        'config_valid': True,
        'ready_for_queries': True,
        'demo_mode': True
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'API endpoint not found',
            'available_endpoints': ['/api/ask', '/api/status', '/api/examples']
        }), 404
    return render_template('index.html'), 404

if __name__ == '__main__':
    print("=" * 60)
    print("🏛️  BNS Legal Assistant - Demo Mode")
    print("   AI-Powered Legal Consultation System")
    print("=" * 60)
    print("🎭 Running in DEMO mode - using mock responses")
    print("🌐 Open your browser to: http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)