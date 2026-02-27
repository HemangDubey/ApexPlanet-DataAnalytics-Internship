// ── H.O.N.E.Y AI Chatbot ──

let chatOpen = false;

function toggleChat() {
    chatOpen = !chatOpen;
    document.getElementById('chatPanel').classList.toggle('open', chatOpen);
    if (chatOpen) document.getElementById('chatInput').focus();
}

// Send on Enter
document.getElementById('chatInput').addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
});

async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    // Add user message
    appendMessage('user', message);
    input.value = '';
    input.disabled = true;
    document.getElementById('chatSendBtn').disabled = true;

    // Show typing indicator
    const typingId = showTyping();

    try {
        const result = await apiPost('/api/ai/chat', { message });
        removeTyping(typingId);
        appendMessage('assistant', formatAIResponse(result.response));
    } catch (e) {
        removeTyping(typingId);
        appendMessage('assistant', '⚠️ Sorry, I encountered an error. Please try again.');
    } finally {
        input.disabled = false;
        document.getElementById('chatSendBtn').disabled = false;
        input.focus();
    }
}

function appendMessage(role, content) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `<div class="msg-content">${content}</div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function showTyping() {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'chat-msg assistant';
    div.id = 'typing-indicator';
    div.innerHTML = '<div class="chat-typing"><span></span><span></span><span></span></div>';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return 'typing-indicator';
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function formatAIResponse(text) {
    if (!text) return '';
    // Convert markdown-like formatting
    return text
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        .replace(/^- (.+)/gm, '• $1')
        .replace(/^(\d+)\. (.+)/gm, '$1. $2')
        .replace(/\n/g, '<br>');
}
