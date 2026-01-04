// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8001'; // FastAPI backend endpoint

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const welcomeScreen = document.getElementById('welcomeScreen');
const statusText = document.getElementById('status-text');

// State
let conversationHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Frontend initialized, checking backend status...');
    checkBackendStatus();
    messageInput.focus();
});

// Check backend status
async function checkBackendStatus() {
    try {
        // Create timeout controller for better browser compatibility
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            cache: 'no-cache',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Health check response:', data); // Debug log
            
            // Check both true and "true" (string) for compatibility
            if (data.unibot_ready === true || data.unibot_ready === "true" || data.unibot_ready === 1) {
                const docCount = data.knowledge_base_documents || 0;
                statusText.textContent = `Backend online${docCount > 0 ? ` (${docCount} docs)` : ''}`;
                statusText.parentElement.style.background = '#d1fae5';
                statusText.parentElement.style.color = '#065f46';
            } else {
                statusText.textContent = 'Backend initializing...';
                statusText.parentElement.style.background = '#fef3c7';
                statusText.parentElement.style.color = '#92400e';
            }
        } else {
            throw new Error(`Backend returned status ${response.status}`);
        }
    } catch (error) {
        console.error('Health check error:', error); // Debug log
        if (error.name === 'AbortError' || error.name === 'TimeoutError') {
            statusText.textContent = 'Backend timeout';
        } else if (error.message && error.message.includes('Failed to fetch')) {
            statusText.textContent = 'Backend offline';
        } else {
            statusText.textContent = 'Backend offline';
        }
        statusText.parentElement.style.background = '#fee2e2';
        statusText.parentElement.style.color = '#991b1b';
    }
}

// Periodically check backend status every 3 seconds
setInterval(checkBackendStatus, 3000);

// Handle suggested question click
function askQuestion(question) {
    messageInput.value = question;
    sendMessage();
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Hide welcome screen
    welcomeScreen.classList.add('hidden');

    // Add user message to UI
    addMessage('user', message);
    messageInput.value = '';
    sendButton.disabled = true;

    // Show thinking indicator
    const thinkingId = addMessage('bot', 'Thinking...', true);

    try {
        // Check if backend is ready first
        const healthController = new AbortController();
        const healthTimeout = setTimeout(() => healthController.abort(), 2000);
        
        const healthCheck = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'},
            cache: 'no-cache',
            signal: healthController.signal
        });
        
        clearTimeout(healthTimeout);
        
        if (!healthCheck.ok) {
            throw new Error('Backend is not ready. Please wait a moment and try again.');
        }
        
        const healthData = await healthCheck.json();
        if (!healthData.unibot_ready) {
            throw new Error('UniBot is still initializing. Please wait a moment and try again.');
        }
        
        // Call FastAPI backend with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
        
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            cache: 'no-cache',
            signal: controller.signal,
            body: JSON.stringify({
                message: message,
                success_criteria: '',
                history: conversationHistory
            })
        });
        
        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        const result = await response.json();
        
        // Remove thinking indicator
        removeMessage(thinkingId);

        // Process response
        if (result.status === 'success' && result.response) {
            addMessage('bot', result.response);
            conversationHistory = result.history || [];
        } else {
            throw new Error('Invalid response format');
        }

    } catch (error) {
        console.error('Error:', error);
        removeMessage(thinkingId);
        
        let errorMessage = 'Sorry, I encountered an error. ';
        if (error.name === 'AbortError' || error.message.includes('timeout')) {
            errorMessage += 'The request took too long. Please try again with a simpler question.';
        } else if (error.message.includes('not ready') || error.message.includes('initializing')) {
            errorMessage += error.message;
        } else if (error.message.includes('503')) {
            errorMessage += 'The backend server is not ready. Please wait a moment and try again.';
        } else {
            errorMessage += 'Please make sure the backend is running and try again.';
        }
        
        addMessage('bot', errorMessage);
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// Add message to UI
function addMessage(role, content, isThinking = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const messageId = `msg-${Date.now()}-${Math.random()}`;
    messageDiv.id = messageId;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (isThinking) {
        messageContent.className += ' thinking';
        messageContent.textContent = content;
    } else {
        // Format message content (support markdown-like formatting)
        messageContent.innerHTML = formatMessage(content);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    messagesDiv.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return messageId;
}

// Remove message
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Format message content (basic markdown support)
function formatMessage(content) {
    if (!content) return '';

    let formatted = content;

    // Convert markdown links [text](url) to HTML
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

    // Convert **bold** to <strong>
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Convert *italic* to <em>
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    // Convert numbered lists
    formatted = formatted.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');

    // Convert bullet points
    formatted = formatted.replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    return formatted;
}

