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

function loadPlacesData() {
    const urlParams = new URLSearchParams(window.location.search);
    const dataParam = urlParams.get('data');
    
    if (dataParam) {
        const decodedData = decodeURIComponent(dataParam);
        return JSON.parse(decodedData);
    }
    return [];
}

function createHtml(place, index) {
    return `
        <div class="aboutObject">
            <div class="aboutObjHead">
                <div class="objTitle">
                    ${index + 1}. ${place.title}
                </div>
                <div class="coordinates">
                    <div class="street">
                        <svg width="10" height="16" viewBox="0 0 10 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="5" cy="5" r="5" fill="#FF7B00"/>
                            <path d="M5.00016 16L0.66683 7.33333L9.3335 7.33333L5.00016 16Z" fill="#FF7B00"/>
                            <circle cx="5" cy="5.5" r="2.5" fill="white"/>
                        </svg>
                        <span>${place.address}</span>
                    </div>
                    <div class="path">
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        </svg>
                        <a href="https://yandex.ru/maps/?pt=${place.coordinates.lon},${place.coordinates.lat}&z=16&l=map" target="_blank">
                            ${place.coordinates.lat}, ${place.coordinates.lon}
                        </a>
                    </div>
                </div>
            </div>
            <div class="objDescriptionWrapper">
                <div class="objDescription truncatedText">
                    ${place.description.substring(0, 150)}...
                </div>
            </div>
            <div class="ObjFooter" data-text="${place.reason}">
                Почему мне предложили этот объект?
            </div>
        </div>
    `;
}

function renderPlaces() {
    const places = loadPlacesData();
    const container = document.getElementById('placesContainer');
    console.log('Loaded places:', places);
    
    if (places.length === 0) {
        container.innerHTML = '<div class="error">Нет данных о местах</div>';
        return;
    }
    
    container.innerHTML = places.map((place, index) => 
        createHtml(place, index)
    ).join('');

    initMap(places);
}

document.addEventListener('DOMContentLoaded', renderPlaces);