(function () {
  let timerInterval = null;
  let startTime = null;
  let notified = false; // Флаг, чтобы уведомление не спамило

  function startBackgroundTimer(endTimestamp, callback) {
    if (timerInterval) clearInterval(timerInterval);

    timerInterval = setInterval(() => {
      const now = Date.now();
      const timeLeftMs = endTimestamp - now;
      const timeLeft = Math.floor(timeLeftMs / 1000);

      callback(timeLeft);

      // Уведомление только один раз при переходе через 0
      if (timeLeft === 0 && !notified) {
        showBreakNotification();
        notified = true;
      }
    }, 1000);
  }

  async function saveSession() {
    const sessionData = JSON.parse(sessionStorage.getItem('gamebalance_session') || '{}');
    if (!sessionData.gameName || !startTime) return;

    const actualDurationMs = Date.now() - startTime;
    const actualDurationSeconds = actualDurationMs / 1000;
    const hoursPlayed = parseFloat((actualDurationSeconds / 3600).toFixed(2));

    try {
      await fetch('/api/sessions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          game_name: sessionData.gameName,
          hours_played: hoursPlayed,
          mood_score: sessionData.moodScore,
          notes: sessionData.notes
        })
      });
    } catch (error) {
      console.error('Save error:', error);
    }
  }

  window.startTimerWithSave = function(gameName, durationMinutes, moodScore, notes) {
    startTime = Date.now();
    notified = false; // Сброс флага уведомления
    const durationSeconds = durationMinutes * 60;
    const endTime = startTime + durationSeconds;

    sessionStorage.setItem('gamebalance_session', JSON.stringify({
      gameName, durationSeconds, moodScore, notes
    }));

    sessionStorage.setItem('gamebalance_timer', JSON.stringify({
      isRunning: true,
      endTime: endTime,
      durationSeconds: durationSeconds
    }));

    startBackgroundTimer(endTime, (timeLeft) => {
      const display = document.getElementById('timer-display');
      const label = document.getElementById('timer-label');

      if (display) {
        if (timeLeft >= 0) {
          // Обычный режим
          const m = Math.floor(timeLeft / 60);
          const s = timeLeft % 60;
          display.textContent = `${m}:${s.toString().padStart(2, '0')}`;
          display.classList.remove('overtime');
          if (label) label.textContent = 'Осталось времени';
        } else {
          // Режим овертайма (время вышло)
          const overtime = Math.abs(timeLeft);
          const m = Math.floor(overtime / 60);
          const s = overtime % 60;
          display.textContent = `+${m}:${s.toString().padStart(2, '0')}`;
          display.classList.add('overtime');
          if (label) label.textContent = 'Время переработки';
        }
        document.title = display.textContent + ' - GameBalance';
      }
    });
  };

  window.stopTimerManual = async function() {
    if (timerInterval) clearInterval(timerInterval);
    sessionStorage.removeItem('gamebalance_timer');
    await saveSession();
    alert('Сессия сохранена');
    window.location.href = '/stats';
  };

  window.addEventListener('DOMContentLoaded', () => {
    const saved = sessionStorage.getItem('gamebalance_timer');
    if (saved) {
      const state = JSON.parse(saved);
      if (state.isRunning && state.endTime) {
        startTime = state.endTime - (state.durationSeconds * 1000);
        if (Date.now() > state.endTime) notified = true; // Если уже овертайм, не спамить

        startBackgroundTimer(state.endTime, (timeLeft) => {
          const display = document.getElementById('timer-display');
          const label = document.getElementById('timer-label');
          if (display) {
            if (timeLeft >= 0) {
              const m = Math.floor(timeLeft / 60);
              const s = timeLeft % 60;
              display.textContent = `${m}:${s.toString().padStart(2, '0')}`;
              display.classList.remove('overtime');
              if (label) label.textContent = 'Осталось времени';
            } else {
              const overtime = Math.abs(timeLeft);
              const m = Math.floor(overtime / 60);
              const s = overtime % 60;
              display.textContent = `+${m}:${s.toString().padStart(2, '0')}`;
              display.classList.add('overtime');
              if (label) label.textContent = 'Время переработки';
            }
          }
        });
      }
    }
  });

  function showBreakNotification() {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('GameBalance', { body: 'Время вышло. Пора отдохнуть.' });
    }
  }
})();