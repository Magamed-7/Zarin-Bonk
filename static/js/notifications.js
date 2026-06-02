document.addEventListener('DOMContentLoaded', function() {
  // Dropdown toggle
  const notificationBtn = document.getElementById('notification-btn');
  const notificationPanel = document.getElementById('notification-panel');

  if (notificationBtn && notificationPanel) {
    notificationBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      notificationPanel.classList.toggle('notification-panel--open');
    });

    // Close when clicking outside
    document.addEventListener('click', function(e) {
      if (!notificationPanel.contains(e.target) && !notificationBtn.contains(e.target)) {
        notificationPanel.classList.remove('notification-panel--open');
      }
    });
  }

  // Mark as read - AJAX
  function setupMarkReadButtons() {
    const markReadButtons = document.querySelectorAll('.mark-read-btn, .mark-read-panel-btn');

    markReadButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        const form = button.closest('form');
        const notificationId = form.closest('[data-id]').dataset.id;
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

        window.showLoading();
        fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
          },
          body: `csrfmiddlewaretoken=${encodeURIComponent(csrfToken)}`
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Update unread count
            const countElement = document.querySelector('.notification-count');
            if (countElement) {
              if (data.unread_count > 0) {
                countElement.textContent = data.unread_count;
              } else {
                countElement.remove();
              }
            }

            // Remove unread class from notification
            const notificationCard = document.querySelector(`[data-id="${notificationId}"]`);
            if (notificationCard) {
              notificationCard.classList.remove('notification-card--unread', 'notification-panel-item--unread');
              const markBtn = notificationCard.querySelector('.mark-read-btn, .mark-read-panel-btn');
              if (markBtn) {
                markBtn.closest('form').remove();
              }
            }
          }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => window.hideLoading());
      });
    });
  }

  // Mark all as read - AJAX
  function setupMarkAllButtons() {
    const markAllButtons = document.querySelectorAll('.mark-all-btn, .mark-all-panel-btn');

    markAllButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        const form = button.closest('form');
        if (!form) return;

        e.preventDefault();
        e.stopPropagation();

        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

        window.showLoading();
        fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
          },
          body: `csrfmiddlewaretoken=${encodeURIComponent(csrfToken)}`
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Update unread count
            const countElement = document.querySelector('.notification-count');
            if (countElement) {
              countElement.remove();
            }

            // Remove all unread classes
            const unreadCards = document.querySelectorAll('.notification-card--unread, .notification-panel-item--unread');
            unreadCards.forEach(card => {
              card.classList.remove('notification-card--unread', 'notification-panel-item--unread');
              const markBtn = card.querySelector('.mark-read-btn, .mark-read-panel-btn');
              if (markBtn) {
                markBtn.closest('form').remove();
              }
            });

            // Also remove mark all buttons
            document.querySelectorAll('.mark-all-form, .mark-all-panel-form').forEach(el => el.remove());
          }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => window.hideLoading());
      });
    });
  }

  setupMarkReadButtons();
  setupMarkAllButtons();
});
