// Общая логика таймера — работает на всех страницах
(function () {
  let tickInterval = null;

  function startBackgroundTimer(timeLeft, callback) {
    if (tickInterval) clearInterval(tickInterval);

    let current = timeLeft;
    tickInterval = setInterval(() => {
      current--;
      callback(current); // обновляем UI или сохраняем

      if (current <= 0) {
        clearInterval(tickInterval);
        sessionStorage.removeItem('gamebalance_timer');
        alert('⏰ Время вышло! Сделайте перерыв.');
      }
    }, 1000);
  }

  // Запуск при загрузке любой страницы, если таймер активен
  window.addEventListener('DOMContentLoaded', () => {
    const saved = sessionStorage.getItem('gamebalance_timer');
    if (saved) {
      const state = JSON.parse(saved);
      if (state.isRunning) {
        startBackgroundTimer(state.timeLeft, (newTime) => {
          // Сохраняем обновлённое время
          sessionStorage.setItem('gamebalance_timer', JSON.stringify({
            isRunning: true,
            timeLeft: newTime
          }));
        });
      }
    }
  });
})();