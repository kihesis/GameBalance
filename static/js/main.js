// Общая логика таймера — работает на всех страницах
(function () {
  let tickInterval = null;

  function startBackgroundTimer(timeLeft, callback) {
    if (tickInterval) clearInterval(tickInterval);

    let current = timeLeft;
    tickInterval = setInterval(() => {
      current--;
      callback(current);

      if (current <= 0) {
        clearInterval(tickInterval);
        sessionStorage.removeItem('gamebalance_timer');
        alert('⏰ Время вышло! Сделайте перерыв.');
      }
    }, 1000);
  }

  // Запуск при загрузке любой страницы, если таймер активенн
  window.addEventListener('DOMContentLoaded', () => {
    const saved = sessionStorage.getItem('gamebalance_timer');
    if (saved) {
      const state = JSON.parse(saved);
      if (state.isRunning) {
        startBackgroundTimer(state.timeLeft, (newTime) => {
          // Сохранил обновлённое время
          sessionStorage.setItem('gamebalance_timer', JSON.stringify({
            isRunning: true,
            timeLeft: newTime
          }));
        });
      }
    }
  });
})();