document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoading = document.getElementById('btn-loading');
    const apiUrl = chatForm.dataset.apiUrl;

    // Прокрутка вниз при загрузке
    chatMessages.scrollTop = chatMessages.scrollHeight;

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const messageText = messageInput.value.trim();
        if (!messageText) return;
        
        // Блокируем кнопку
        sendBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        
        // Добавляем сообщение пользователя в чат сразу
        addMessage(messageText, 'user');
        messageInput.value = '';
        
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
            if (data.success) {
                addMessage(data.message, 'ai');
            } else {
                addMessage('Ошибка: ' + data.error, 'ai');
            }
        })
        .catch(error => {
            console.error('Error:', error);
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
