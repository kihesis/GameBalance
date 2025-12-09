// static/service-worker.js
self.addEventListener('message', (event) => {
    if (event.data.action === 'startTimer') {
        const duration = event.data.duration || 50 * 60; // в секундах
        let countdown = duration;

        const interval = setInterval(() => {
            countdown--;
            if (countdown <= 0) {
                clearInterval(interval);
                self.registration.showNotification('GameBalance', {
                    body: '⏰ Время вышло! Сделайте перерыв.',
                    icon: '/static/images/icon.png'
                });
            }
        }, 1000);
    }
});