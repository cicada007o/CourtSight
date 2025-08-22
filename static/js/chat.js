// BNS Legal Assistant - Chat Interface JavaScript

// Chat-specific global variables
let chatHistory = [];
let sessionStats = {
    questions: 0,
    totalConfidence: 0
};
let isProcessingQuery = false;

// Initialize chat functionality
function initializeChat() {
    const queryInput = document.getElementById('query-input');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('chat-messages');
    
    if (!queryInput || !sendButton || !messagesContainer) {
        console.error('Chat elements not found');
        return;
    }
    
    // Set up event listeners
    setupChatEventListeners();
    
    // Load chat history from session storage
    loadChatHistory();
    
    // Focus on input if system is ready
    if (systemStatus.ready_for_queries) {
        queryInput.focus();
    }
    
    // Auto-scroll to bottom
    scrollToBottom();
}

function setupChatEventListeners() {
    const queryInput = document.getElementById('query-input');
    const sendButton = document.getElementById('send-button');
    
    // Send button click
    sendButton.addEventListener('click', sendQuery);
    
    // Enter key to send (Shift+Enter for new line)
    queryInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery();
        }
    });
    
    // Character counter
    queryInput.addEventListener('input', updateCharacterCounter);
    
    // Auto-resize textarea
    queryInput.addEventListener('input', autoResizeTextarea);
    
    // Paste event handler
    queryInput.addEventListener('paste', function(e) {
        setTimeout(() => {
            updateCharacterCounter();
            autoResizeTextarea();
        }, 10);
    });
}

function sendQuery() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value.trim();
    
    if (!query || isProcessingQuery) {
        return;
    }
    
    if (!systemStatus.ready_for_queries) {
        showAlert('System is not ready yet. Please wait for initialization to complete.', 'warning');
        return;
    }
    
    if (query.length > 1000) {
        showAlert('Query is too long. Please limit to 1000 characters.', 'danger');
        return;
    }
    
    // Disable input and show processing state
    setProcessingState(true);
    
    // Add user message to chat
    addMessage(query, 'user');
    
    // Show typing indicator
    showTypingIndicator();
    
    // Clear input
    queryInput.value = '';
    updateCharacterCounter();
    autoResizeTextarea();
    
    // Send request to API
    fetch('/api/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        handleQueryResponse(query, data);
    })
    .catch(error => {
        console.error('Error sending query:', error);
        handleQueryError(error);
    })
    .finally(() => {
        hideTypingIndicator();
        setProcessingState(false);
    });
}

function handleQueryResponse(query, data) {
    if (data.success) {
        // Add successful response to chat
        addMessage(data.answer, 'assistant', {
            confidence: data.confidence,
            sections_cited: data.sections_cited || [],
            query_type: data.query_type,
            retrieved_docs: data.retrieved_docs || 0,
            source_documents: data.source_documents || []
        });
        
        // Update session stats
        updateSessionStats(data.confidence || 0);
        
        // Save to chat history
        saveChatEntry(query, data);
        
        // Show success feedback
        if (data.confidence < 0.3) {
            showAlert('Response generated with low confidence. Consider rephrasing your query or consulting a legal professional.', 'warning');
        }
    } else {
        // Handle API errors
        const errorMessage = data.error || 'Failed to process your query. Please try again.';
        addMessage(`Sorry, I encountered an error: ${errorMessage}`, 'assistant', { error: true });
        showAlert(errorMessage, 'danger');
    }
}

function handleQueryError(error) {
    const errorMessage = 'Network error occurred. Please check your connection and try again.';
    addMessage(`Sorry, I couldn't process your request due to a network error. Please try again.`, 'assistant', { error: true });
    showAlert(errorMessage, 'danger');
}

function addMessage(content, sender, metadata = {}) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    let messageContent = '';
    
    if (sender === 'user') {
        messageContent = `<div class="message-content">${escapeHtml(content)}</div>`;
    } else {
        // Assistant message with metadata
        messageContent = `<div class="message-content">${formatAssistantMessage(content)}</div>`;
        
        if (metadata.confidence !== undefined && !metadata.error) {
            const confidenceClass = getConfidenceClass(metadata.confidence);
            const confidencePercent = Math.round(metadata.confidence * 100);
            messageContent += `
                <div class="confidence-badge">
                    <span class="badge ${confidenceClass}">
                        <i class="fas fa-chart-line"></i> ${confidencePercent}% Confidence
                    </span>
                </div>
            `;
        }
        
        if (metadata.sections_cited && metadata.sections_cited.length > 0) {
            messageContent += `
                <div class="source-citation">
                    <strong class="section-ref">Sections Referenced:</strong>
                    ${metadata.sections_cited.map(section => `<span class="badge bg-secondary me-1">${section}</span>`).join('')}
                </div>
            `;
        }
        
        if (metadata.query_type && !metadata.error) {
            messageContent += `
                <div class="mt-2">
                    <small class="text-muted">
                        <i class="fas fa-tag me-1"></i>Query Type: ${metadata.query_type} | 
                        <i class="fas fa-file-text me-1"></i>Sources: ${metadata.retrieved_docs || 0}
                    </small>
                </div>
            `;
        }
    }
    
    messageDiv.innerHTML = messageContent;
    messagesContainer.appendChild(messageDiv);
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp text-muted small mt-1';
    timestamp.textContent = new Date().toLocaleTimeString();
    messageDiv.appendChild(timestamp);
    
    // Scroll to bottom
    scrollToBottom();
}

function formatAssistantMessage(content) {
    // Convert newlines to paragraphs
    let formatted = escapeHtml(content);
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    formatted = `<p>${formatted}</p>`;
    
    // Format section references
    formatted = formatted.replace(/Section (\d+)/g, '<strong>Section $1</strong>');
    
    // Format legal terms
    const legalTerms = ['BNS', 'IPC', 'CrPC', 'Constitution', 'Supreme Court', 'High Court'];
    legalTerms.forEach(term => {
        const regex = new RegExp(`\\b(${term})\\b`, 'gi');
        formatted = formatted.replace(regex, '<strong>$1</strong>');
    });
    
    return formatted;
}

function getConfidenceClass(confidence) {
    if (confidence >= 0.7) return 'bg-success confidence-high';
    if (confidence >= 0.4) return 'bg-warning confidence-medium';
    return 'bg-danger confidence-low';
}

function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'block';
        scrollToBottom();
    }
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

function setProcessingState(processing) {
    const queryInput = document.getElementById('query-input');
    const sendButton = document.getElementById('send-button');
    
    isProcessingQuery = processing;
    
    if (queryInput) {
        queryInput.disabled = processing;
    }
    
    if (sendButton) {
        sendButton.disabled = processing;
        if (processing) {
            addLoadingState(sendButton);
        } else {
            removeLoadingState(sendButton);
        }
    }
}

function updateCharacterCounter() {
    const queryInput = document.getElementById('query-input');
    const counter = document.getElementById('char-counter');
    
    if (queryInput && counter) {
        const length = queryInput.value.length;
        counter.textContent = length;
        
        // Change color based on length
        if (length > 900) {
            counter.className = 'text-danger';
        } else if (length > 800) {
            counter.className = 'text-warning';
        } else {
            counter.className = 'text-muted';
        }
    }
}

function autoResizeTextarea() {
    const textarea = document.getElementById('query-input');
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function updateSessionStats(confidence) {
    sessionStats.questions++;
    sessionStats.totalConfidence += confidence;
    
    const avgConfidence = sessionStats.totalConfidence / sessionStats.questions;
    
    // Update UI
    const questionsElement = document.getElementById('questions-count');
    const confidenceElement = document.getElementById('avg-confidence');
    
    if (questionsElement) {
        questionsElement.textContent = sessionStats.questions;
    }
    
    if (confidenceElement) {
        confidenceElement.textContent = Math.round(avgConfidence * 100) + '%';
        confidenceElement.className = 'fw-bold ' + (avgConfidence >= 0.7 ? 'text-success' : avgConfidence >= 0.4 ? 'text-warning' : 'text-danger');
    }
}

function saveChatEntry(query, response) {
    const entry = {
        query: query,
        answer: response.answer,
        confidence: response.confidence || 0,
        sections_cited: response.sections_cited || [],
        query_type: response.query_type || 'unknown',
        timestamp: new Date().toISOString()
    };
    
    chatHistory.push(entry);
    
    // Save to session storage
    try {
        sessionStorage.setItem('bns_chat_history', JSON.stringify(chatHistory));
    } catch (error) {
        console.error('Failed to save chat history:', error);
    }
}

function loadChatHistory() {
    try {
        const saved = sessionStorage.getItem('bns_chat_history');
        if (saved) {
            chatHistory = JSON.parse(saved);
            
            // Restore session stats
            if (chatHistory.length > 0) {
                sessionStats.questions = chatHistory.length;
                sessionStats.totalConfidence = chatHistory.reduce((sum, entry) => sum + (entry.confidence || 0), 0);
                updateSessionStats(0); // Update UI without adding to stats
            }
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
        chatHistory = [];
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export chat functions
window.BNSChat = {
    sendQuery,
    addMessage,
    clearChat: () => {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = `
                <div class="message system">
                    <i class="fas fa-robot me-2"></i>
                    Chat cleared. How can I help you with BNS legal questions?
                </div>
            `;
        }
        chatHistory = [];
        sessionStats = { questions: 0, totalConfidence: 0 };
        updateSessionStats(0);
        
        try {
            sessionStorage.removeItem('bns_chat_history');
        } catch (error) {
            console.error('Failed to clear chat history:', error);
        }
    },
    getChatHistory: () => chatHistory,
    getSessionStats: () => sessionStats
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChat);
} else {
    initializeChat();
}