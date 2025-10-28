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



