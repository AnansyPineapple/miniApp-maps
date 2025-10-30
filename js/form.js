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


const hoursDropdown = document.getElementById('hoursDropdown');
const hoursSelected = document.getElementById('hoursSelected');
const hoursList = document.getElementById('hoursList');
let selectedHours = '';

function setHoursEmptyState() {
    if (!selectedHours) {
        hoursSelected.textContent = '';
        hoursSelected.classList.add('empty');
    } else {
        hoursSelected.classList.remove('empty');
    }
}
setHoursEmptyState();
hoursSelected.addEventListener('click', () => {
    hoursDropdown.classList.toggle('open');
});
hoursList.querySelectorAll('.dropdownItem').forEach(item => {
    item.addEventListener('click', () => {
        selectedHours = item.dataset.value;
        hoursSelected.textContent = item.textContent;
        hoursDropdown.classList.remove('open');
        hoursSelected.classList.remove('error');
        setHoursEmptyState();
    });
});
document.addEventListener('click', (e) => {
    if (!hoursDropdown.contains(e.target)) {
        hoursDropdown.classList.remove('open');
    }
});

// Кастомный dropdown для минут
const minutesDropdown = document.getElementById('minutesDropdown');
const minutesSelected = document.getElementById('minutesSelected');
const minutesList = document.getElementById('minutesList');
let selectedMinutes = '';

function setMinutesEmptyState() {
    if (!selectedMinutes) {
        minutesSelected.textContent = '';
        minutesSelected.classList.add('empty');
    } else {
        minutesSelected.classList.remove('empty');
    }
}
setMinutesEmptyState();
minutesSelected.addEventListener('click', () => {
    minutesDropdown.classList.toggle('open');
});
minutesList.querySelectorAll('.dropdownItem').forEach(item => {
    item.addEventListener('click', () => {
        selectedMinutes = item.dataset.value;
        minutesSelected.textContent = item.textContent;
        minutesDropdown.classList.remove('open');
        minutesSelected.classList.remove('error');
        setMinutesEmptyState();
    });
});
document.addEventListener('click', (e) => {
    if (!minutesDropdown.contains(e.target)) {
        minutesDropdown.classList.remove('open');
    }
});

document.getElementById('routeForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  console.log("Кнопка нажата");

  // Проверка выбора
  if (!selectedHours) {
    hoursSelected.classList.add('error');
    hoursDropdown.classList.add('open');
    return;
  }
  if (!selectedMinutes) {
    minutesSelected.classList.add('error');
    minutesDropdown.classList.add('open');
    return;
  }

  const data = {
    query: firstTextarea.value,
    hours: selectedHours,
    minutes: selectedMinutes,
    startPoint: thirdTextarea.value
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