document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoading = document.getElementById('btn-loading');
    const apiUrl = chatForm.dataset.apiUrl;

    // Прокрутка вниз при загрузке
    scrollToBottom();

    // Авто-ресайз textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const messageText = messageInput.value.trim();
        if (!messageText) return;
        
        // Удаляем empty-chat если есть
        const emptyChat = chatMessages.querySelector('.empty-chat');
        if (emptyChat) emptyChat.remove();
        
        // Блокируем кнопку
        sendBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
        
        // Добавляем сообщение пользователя в чат сразу
        addMessage(messageText, 'user');
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Показываем индикатор печатания
        const typingIndicator = addTypingIndicator();
        
        // Отправляем запрос
        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                message: messageText
            })
        })
        .then(response => response.json())
        .then(data => {
            // Удаляем индикатор печатания
            removeTypingIndicator(typingIndicator);
            
            if (data.success) {
                addMessage(data.message, 'ai');
            } else {
                addMessage('Ошибка: ' + data.error, 'ai');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Удаляем индикатор печатания
            removeTypingIndicator(typingIndicator);
            addMessage('Произошла ошибка при отправке сообщения.', 'ai');
        })
        .finally(() => {
            // Разблокируем кнопку
            sendBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
        });
    });

    function addMessage(text, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const now = new Date();
        const time = now.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="sender">${role === 'user' ? '👤 Вы' : '🤖 Ассистент'}</span>
                <span class="time">${time}</span>
            </div>
            <p class="message-text">${escapeHtml(text)}</p>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
        return typingDiv;
    }
    
    function removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.style.opacity = '0';
            indicator.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function getCSRFToken() {
        const name = 'csrftoken';
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    }
});
