const modalOverlay = document.getElementById('modalOverlay');
const modalText = document.querySelector('.modalText');
const modalCloseBtn = document.getElementById('modalCloseBtn');

document.querySelectorAll('.ObjFooter').forEach(el => {
    el.addEventListener('click', () => {
        // Подставить текст для объекта
        modalText.textContent = el.dataset.text;

        modalOverlay.style.display = 'flex';
        setTimeout(() => {
            modalOverlay.classList.add('active'); 
        }, 10);
    });
});

modalCloseBtn.addEventListener('click', () => {
    modalOverlay.classList.remove('active');
    setTimeout(() => {
        modalOverlay.style.display = 'none';
    }, 300);
});

modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
        modalOverlay.classList.remove('active');
        setTimeout(() => {
            modalOverlay.style.display = 'none';
        }, 300);
    }
});


const modalOverlayDesc = document.getElementById('modalOverlayDesc');
const modalHeaderDesc = document.getElementById('modalHeaderDesc');
const modalTextDesc = document.getElementById('modalTextDesc');
const modalCloseBtnDesc = document.getElementById('modalCloseBtnDesc');

// document.querySelectorAll('.truncatedText').forEach(el => {
//     el.addEventListener('click', () => {
//         const obj = el.closest('.aboutObject');
//         const title = obj.querySelector('.objTitle').textContent;
//         const text = el.textContent;
//         modalHeaderDesc.textContent = title;
//         modalTextDesc.textContent = text;
//         modalOverlayDesc.style.display = 'flex';
//         setTimeout(() => modalOverlayDesc.classList.add('active'), 10);
//     });
// });

document.querySelectorAll('.objDescription').forEach(el => {
    el.addEventListener('click', () => {
        const obj = el.closest('.aboutObject'); 
        const title = obj.querySelector('.objTitle').textContent; 
        const text = el.textContent; 

        modalHeaderDesc.textContent = title;
        modalTextDesc.textContent = text;

        modalOverlayDesc.style.display = 'flex';
        setTimeout(() => {
            modalOverlayDesc.classList.add('active');
        }, 10);
    });
});

modalCloseBtnDesc.addEventListener('click', () => {
    modalOverlayDesc.classList.remove('active');
    setTimeout(() => {
        modalOverlayDesc.style.display = 'none';
    }, 300);
});

modalOverlayDesc.addEventListener('click', (e) => {
    if (e.target === modalOverlayDesc) {
        modalOverlayDesc.classList.remove('active');
        setTimeout(() => {
            modalOverlayDesc.style.display = 'none';
        }, 300);
    }
});


//ставит индексы у объектов!!!!!
document.querySelectorAll('.aboutObject .objTitle').forEach((el, index) => {
    el.textContent = `${index + 1}. ${el.textContent}`;
});



document.querySelector('.buttonsCont button:last-child').addEventListener('click', () => {
    const objects = document.querySelectorAll('.aboutObject');
    let textToCopy = '';

    objects.forEach((obj, index) => {
        const title = obj.querySelector('.objTitle').innerText.trim();
        const street = obj.querySelector('.street span')?.innerText.trim() || '';
        const coords = obj.querySelector('.path a')?.innerText.trim() || '';
        const description = obj.querySelector('.objDescription')?.dataset.fullText || obj.querySelector('.objDescription')?.innerText.trim();
        const reason = obj.querySelector('.ObjFooter')?.dataset.text.trim() || '';

        textToCopy += `${title}\n`;
        textToCopy += `Адрес: ${street}\n`;
        textToCopy += `Координаты: ${coords}\n`;
        textToCopy += `Описание: ${description}\n`;
        textToCopy += `Почему предложили: ${reason}\n\n`;
    });

    navigator.clipboard.writeText(textToCopy)
        .then(() => {
            alert('Текст скопирован в буфер обмена!');
        })
        .catch(err => {
            console.error('Не удалось скопировать текст: ', err);
        });
});


document.querySelector('.buttonsCont button:first-child').addEventListener('click', () => {
    window.location.href = 'index.html';
});