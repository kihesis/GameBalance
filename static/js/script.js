// GameBalance — Frontend logic
document.addEventListener('DOMContentLoaded', function () {
    // Пример: добавление минимальной валидации (опционально)
    const logForm = document.querySelector('form[action="/log"]');
    if (logForm) {
        logForm.addEventListener('submit', function(e) {
            const hoursInput = document.getElementById('hours');
            const moodInputs = document.querySelectorAll('input[name="mood"]');

            let moodSelected = false;
            moodInputs.forEach(input => {
                if (input.checked) moodSelected = true;
            });

            if (!hoursInput.value || parseFloat(hoursInput.value) <= 0) {
                e.preventDefault();
                alert('Укажите корректное количество часов.');
                return;
            }

            if (!moodSelected) {
                e.preventDefault();
                alert('Выберите настроение.');
            }
        });
    }

    // Другая логика может быть добавлена позже (например, Chart.js)
});