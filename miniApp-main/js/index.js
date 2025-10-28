function autoResizeTextarea(textarea, keepDefault = false) {
    if (keepDefault && textarea.value.trim() === '') return;

    textarea.style.height = 'auto'; 
    const maxHeight = parseInt(getComputedStyle(textarea).maxHeight);
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = newHeight + 'px';
}

const firstTextarea = document.getElementById('firstQuestion');
if (firstTextarea) {
    autoResizeTextarea(firstTextarea);
    firstTextarea.addEventListener('input', () => autoResizeTextarea(firstTextarea));
}

const thirdTextarea = document.getElementById('thirdQuestion');
if (thirdTextarea) {
    thirdTextarea.addEventListener('input', () => autoResizeTextarea(thirdTextarea, true));
}


const hoursSelect = document.getElementById('hoursChoice');
const minutesSelect = document.getElementById('minutesChoice');

// Часы: 1–5 
for(let i = 1; i <= 5; i++){
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = i;
    hoursSelect.appendChild(opt);
}

// Минуты: 15, 30, 45
[15, 30, 45].forEach(min => {
    const opt = document.createElement('option');
    opt.value = min;
    opt.textContent = min;
    minutesSelect.appendChild(opt);
});

document.getElementById('routeForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const data = {
    query: document.getElementById('firstQuestion').value,
    hours: document.getElementById('hoursChoice').value,
    minutes: document.getElementById('minutesChoice').value,
    startPoint: document.getElementById('thirdQuestion').value
  };

  const response = await fetch('https://map-bot-3rhu.onrender.com/generate_route', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });

  const result = await response.json();
  localStorage.setItem('routeData', JSON.stringify(result));

  window.location.href = 'answer.html';
});