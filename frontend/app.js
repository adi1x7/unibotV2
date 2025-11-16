// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000'; // FastAPI backend endpoint

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
    checkBackendStatus();
    messageInput.focus();
});

// Check backend status
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            if (data.unibot_ready) {
                statusText.textContent = 'Backend online';
                statusText.parentElement.style.background = '#d1fae5';
                statusText.parentElement.style.color = '#065f46';
            } else {
                statusText.textContent = 'Backend initializing...';
                statusText.parentElement.style.background = '#fef3c7';
                statusText.parentElement.style.color = '#92400e';
            }
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        statusText.textContent = 'Backend offline';
        statusText.parentElement.style.background = '#fee2e2';
        statusText.parentElement.style.color = '#991b1b';
    }
}

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
        // Call FastAPI backend
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                success_criteria: '',
                history: conversationHistory
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to get response');
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
        addMessage('bot', 'Sorry, I encountered an error. Please make sure the backend is running and try again.');
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

