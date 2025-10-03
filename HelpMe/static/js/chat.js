let chatSocket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const messagesContainer = document.querySelector('.messages');
const messageInput = document.querySelector('#messageInput');
const chatForm = document.querySelector('#chatForm');

function connectWebSocket() {
const wsScheme = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const wsPath = '/ws/chat/{{ ticket.id }}/';
const wsUrl = wsScheme + window.location.host + wsPath;
console.log('Attempting WebSocket connection to:', wsUrl);

// Close existing connection if any
if (chatSocket) {
    chatSocket.close();
}

try {
    chatSocket = new WebSocket(wsUrl);
    let pingInterval;

chatSocket.onopen = function(e) {
    console.log('WebSocket connection established');
    reconnectAttempts = 0;
    messageInput.disabled = false;
    messageInput.placeholder = 'Type your message...';
    
    // Start sending ping every 30 seconds
    pingInterval = setInterval(() => {
    if (chatSocket.readyState === WebSocket.OPEN) {
        chatSocket.send(JSON.stringify({ 'type': 'ping' }));
    }
    }, 30000);
};

chatSocket.onmessage = function(e) {
    try {
    const data = JSON.parse(e.data);
    
    // Handle ping/pong
    if (data.type === 'pong') {
        console.log('Received pong from server');
        return;
    }
    
    if (data.error) {
        console.error('Message error:', data.error);
        return;
    }

    const message = data.message;
    const username = data.username;
    const timestamp = data.timestamp || new Date().toLocaleString();
    const isCurrentUser = username === '{{ request.user.username }}';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isCurrentUser ? 'self' : 'other'}`;
    
    const senderDiv = document.createElement('div');
    senderDiv.className = 'sender';
    senderDiv.textContent = username;
    
    const textDiv = document.createElement('div');
    textDiv.className = 'text';
    textDiv.textContent = message;
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'time';
    timeSpan.textContent = timestamp;
    
    textDiv.appendChild(timeSpan);
    messageDiv.appendChild(senderDiv);
    messageDiv.appendChild(textDiv);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    } catch (error) {
    console.error('Error processing message:', error);
    }
};

chatSocket.onclose = function(e) {
    console.log('WebSocket closed. Code:', e.code, 'Reason:', e.reason);
    messageInput.disabled = true;
    messageInput.placeholder = 'Connection lost. Reconnecting...';
    
    // Clear ping interval
    if (pingInterval) {
    clearInterval(pingInterval);
    }
    
    if (reconnectAttempts < maxReconnectAttempts) {
    reconnectAttempts++;
    console.log(`Reconnect attempt ${reconnectAttempts} of ${maxReconnectAttempts}`);
    setTimeout(connectWebSocket, 2000 * Math.min(reconnectAttempts, 10));
    } else {
    messageInput.placeholder = 'Connection failed. Please check your connection and refresh.';
    console.log('Max reconnection attempts reached. Please refresh the page.');
    }
};

chatSocket.onerror = function(e) {
    console.error('WebSocket error occurred:', e);
    console.log('Current connection state:', chatSocket.readyState);
    messageInput.disabled = true;
    
    if (chatSocket.readyState === WebSocket.CLOSED) {
    console.log('Connection is closed. Verifying credentials...');
    // You might want to verify your session is still valid
    fetch('/ws/chat/{{ ticket.id }}/')
        .then(response => {
        if (!response.ok) {
            messageInput.placeholder = 'Please check your login status and permissions.';
            throw new Error('Authentication check failed');
        }
        })
        .catch(error => console.error('Auth check failed:', error));
    }
};
} catch (error) {
    console.error('Error creating WebSocket connection:', error);
    messageInput.disabled = true;
    messageInput.placeholder = 'Connection failed. Please refresh the page.';
}
}

chatForm.onsubmit = function(e) {
e.preventDefault();
const message = messageInput.value.trim();

if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(JSON.stringify({
    'message': message
    }));
    messageInput.value = '';
}
};

// Initial connection
connectWebSocket();

// Scroll to bottom on load
messagesContainer.scrollTop = messagesContainer.scrollHeight;

// Clean up on page unload
window.onbeforeunload = function() {
if (chatSocket) {
    chatSocket.close();
}
};