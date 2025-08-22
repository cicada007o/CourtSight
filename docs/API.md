# BNS Legal Assistant - API Documentation

Complete API reference for the BNS Legal Assistant RESTful API endpoints.

## Base URL

```
http://localhost:5000
```

## Authentication

No authentication is required for local deployment. For production, consider implementing API key authentication.

## Response Format

All API responses follow this standard format:

```json
{
    "success": true|false,
    "data": {},
    "error": "error message if success is false",
    "timestamp": "2023-12-01T10:30:00Z"
}
```

---

## Endpoints

### 1. Ask Legal Question

**Endpoint**: `POST /api/ask`

**Description**: Submit a legal question and receive an AI-generated response based on BNS documents.

#### Request

```http
POST /api/ask
Content-Type: application/json

{
    "query": "What is the definition of theft under BNS?"
}
```

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | Yes | Legal question (max 1000 characters) |

#### Response

```json
{
    "success": true,
    "answer": "According to the Bharatiya Nyaya Sanhita (BNS) 2023, theft is defined in Section 303...",
    "confidence": 0.85,
    "retrieved_docs": 3,
    "query_type": "definition",
    "sections_cited": ["Section 303", "Section 304"],
    "model_used": "gpt-3.5-turbo",
    "source_documents": [
        {
            "text": "Excerpt from relevant document...",
            "section": "303",
            "content_type": "definition",
            "relevance_score": 0.92
        }
    ],
    "session_id": "uuid-string",
    "question_number": 1,
    "timestamp": "2023-12-01T10:30:00Z"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether the request was successful |
| answer | string | AI-generated legal response |
| confidence | float | Confidence score (0-1) |
| retrieved_docs | integer | Number of documents used |
| query_type | string | Classified query type |
| sections_cited | array | BNS sections referenced |
| source_documents | array | Source document excerpts |
| session_id | string | Session identifier |
| question_number | integer | Question count in session |

#### Error Response

```json
{
    "success": false,
    "error": "System not initialized. Please wait for initialization to complete.",
    "initialization_status": {
        "status": "in_progress",
        "message": "Processing BNS documents..."
    }
}
```

#### Status Codes

- `200 OK` - Successful query processing
- `400 Bad Request` - Invalid query or missing parameters
- `503 Service Unavailable` - System not ready

---

### 2. System Status

**Endpoint**: `GET /api/status`

**Description**: Get comprehensive system health and status information.

#### Request

```http
GET /api/status
```

#### Response

```json
{
    "overall_status": "healthy",
    "ready_for_queries": true,
    "initialization_status": {
        "status": "completed",
        "message": "System initialized successfully",
        "document_count": 1250
    },
    "vector_store": {
        "status": "healthy",
        "document_count": 1250,
        "collection_accessible": true,
        "embedding_generation": true,
        "search_functionality": true,
        "openai_api": true
    },
    "openai_api": "healthy",
    "collection_stats": {
        "total_documents": 1250,
        "content_types": {
            "definition": 245,
            "penalty": 189,
            "procedure": 156,
            "general": 660
        },
        "sources": ["bns-2023-main.pdf", "bns-appendix.pdf"],
        "collection_name": "bns_legal_documents",
        "embedding_model": "text-embedding-ada-002"
    },
    "config": {
        "openai_model": "gpt-3.5-turbo",
        "chunk_size": 800,
        "max_retrieval_docs": 5,
        "similarity_threshold": 0.7
    },
    "timestamp": "2023-12-01T10:30:00Z"
}
```

#### Status Values

- `healthy` - All systems operational
- `initializing` - System starting up
- `unhealthy` - System errors detected

---

### 3. Initialize System

**Endpoint**: `POST /api/initialize`

**Description**: Manually trigger system reinitialization.

#### Request

```http
POST /api/initialize
```

#### Response

```json
{
    "success": true,
    "message": "System reinitialization started",
    "status": {
        "status": "in_progress",
        "message": "Initializing system components..."
    }
}
```

---

### 4. Example Queries

**Endpoint**: `GET /api/examples`

**Description**: Get predefined example queries for different legal categories.

#### Request

```http
GET /api/examples
```

#### Response

```json
{
    "success": true,
    "examples": [
        {
            "category": "Definitions",
            "query": "What is the definition of theft under BNS?",
            "description": "Get clear definitions of legal terms and concepts"
        },
        {
            "category": "Penalties",
            "query": "What is the punishment for assault under BNS?",
            "description": "Learn about specific penalties and punishments"
        }
    ]
}
```

---

### 5. Health Check

**Endpoint**: `GET /health`

**Description**: Simple health check endpoint for monitoring systems.

#### Request

```http
GET /health
```

#### Response

```json
{
    "status": "healthy",
    "timestamp": "2023-12-01T10:30:00Z",
    "initialization_status": {
        "status": "completed",
        "message": "System ready"
    },
    "config_valid": true,
    "ready_for_queries": true
}
```

---

## Query Types

The system automatically classifies queries into these types:

| Type | Description | Example |
|------|-------------|---------|
| definition | Questions about legal term definitions | "What is theft?" |
| penalty | Questions about punishments/sentences | "What is the punishment for theft?" |
| procedure | Questions about legal processes | "How to file a complaint?" |
| general | General legal questions | "Rights of accused person" |

---

## Error Handling

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | Bad Request | Invalid query format or parameters |
| 404 | Not Found | Endpoint not found |
| 500 | Internal Error | Server processing error |
| 503 | Service Unavailable | System not ready/initialized |

### Error Response Format

```json
{
    "success": false,
    "error": "Descriptive error message",
    "details": "Additional error details (debug mode only)",
    "timestamp": "2023-12-01T10:30:00Z"
}
```

---

## Usage Examples

### Python Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:5000"

# Check system status
response = requests.get(f"{base_url}/api/status")
status = response.json()
print(f"System ready: {status['ready_for_queries']}")

# Ask a legal question
if status['ready_for_queries']:
    query_data = {
        "query": "What is the definition of theft under BNS?"
    }
    
    response = requests.post(
        f"{base_url}/api/ask",
        headers={"Content-Type": "application/json"},
        data=json.dumps(query_data)
    )
    
    result = response.json()
    if result['success']:
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Sections: {', '.join(result['sections_cited'])}")
    else:
        print(f"Error: {result['error']}")
```

### JavaScript Example

```javascript
// Check system status
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        return status.ready_for_queries;
    } catch (error) {
        console.error('Status check failed:', error);
        return false;
    }
}

// Ask legal question
async function askLegalQuestion(query) {
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('Answer:', result.answer);
            console.log('Confidence:', Math.round(result.confidence * 100) + '%');
            console.log('Sections:', result.sections_cited.join(', '));
        } else {
            console.error('Query failed:', result.error);
        }
        
        return result;
    } catch (error) {
        console.error('Request failed:', error);
        return { success: false, error: error.message };
    }
}

// Usage
(async () => {
    if (await checkSystemStatus()) {
        await askLegalQuestion("What is the punishment for theft?");
    } else {
        console.log("System not ready yet");
    }
})();
```

### cURL Examples

```bash
# Check system status
curl -X GET http://localhost:5000/api/status

# Ask a legal question
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the definition of theft under BNS?"}'

# Get example queries
curl -X GET http://localhost:5000/api/examples

# Health check
curl -X GET http://localhost:5000/health
```

---

## Rate Limiting

Currently, no rate limiting is implemented for local deployment. For production use, consider implementing rate limiting based on:

- Requests per minute per IP
- Requests per hour per session
- Query complexity limits

---

## API Versioning

The current API is version 1.0. Future versions will be accessible via:

```
/api/v1/ask
/api/v2/ask
```

---

## WebSocket Support (Future)

Real-time chat functionality will be available via WebSocket connections:

```javascript
// Future implementation
const ws = new WebSocket('ws://localhost:5000/ws/chat');
ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    // Handle real-time response
};
```

---

## Support and Feedback

For API support:
- Check application logs: `bns_legal_assistant.log`
- Enable debug mode: `FLASK_DEBUG=True`
- Review system status endpoint for health information
- Consult troubleshooting documentation