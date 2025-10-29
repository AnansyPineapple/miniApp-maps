const routeData = JSON.parse(localStorage.getItem('routeData'));

if (routeData && routeData.places) {
  const container = document.querySelector('.ansContainer');
  container.innerHTML = '<div class="mapBlock"><div class="mainMap" id="map"></div></div>';

  routeData.places.forEach((place, index) => {
    const html = `
      <div class="aboutObject">
        <div class="aboutObjHead">
          <div class="objTitle">
            ${place.title}
          </div>
          <div class="coordinates">
            <div class="street">
                <svg width="10" height="16" viewBox="0 0 10 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="5" cy="5" r="5" fill="#FF7B00"></circle>
                    <path d="M5.00016 16L0.66683 7.33333L9.3335 7.33333L5.00016 16Z" fill="#FF7B00"></path>
                    <circle cx="5" cy="5.5" r="2.5" fill="white"></circle>
                </svg>
                <span>${place.address}</span>
            </div>
            <div class="path">
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                     <path d="M14 8C14 11.3137 11.3137 14 8 14C4.68629 14 2 11.3137 2 8C2 4.68629 4.68629 2 8 2C11.3137 2 14 4.68629 14 8ZM2.99207 8C2.99207 10.7658 5.2342 13.0079 8 13.0079C10.7658 13.0079 13.0079 10.7658 13.0079 8C13.0079 5.2342 10.7658 2.99207 8 2.99207C5.2342 2.99207 2.99207 5.2342 2.99207 8Z" fill="#FF7B00"></path>
                    <path d="M11 8C11 9.65685 9.65685 11 8 11C6.34315 11 5 9.65685 5 8C5 6.34315 6.34315 5 8 5C9.65685 5 11 6.34315 11 8ZM5.9696 8C5.9696 9.12136 6.87864 10.0304 8 10.0304C9.12136 10.0304 10.0304 9.12136 10.0304 8C10.0304 6.87864 9.12136 5.9696 8 5.9696C6.87864 5.9696 5.9696 6.87864 5.9696 8Z" fill="#FF7B00"></path>
                    <line x1="2.66675" y1="8.22222" x2="8.12813e-05" y2="8.22222" stroke="#FF7B00" stroke-width="0.444444"></line>
                    <line x1="-1.29515e-08" y1="7.77778" x2="2.66667" y2="7.77778" stroke="#FF7B00" stroke-width="0.444444"></line>
                    <line x1="16" y1="8.22222" x2="13.3333" y2="8.22222" stroke="#FF7B00" stroke-width="0.444444"></line>
                    <line x1="13.3333" y1="7.77778" x2="15.9999" y2="7.77778" stroke="#FF7B00" stroke-width="0.444444"></line>
                    <line x1="7.77778" y1="2.66666" x2="7.77778" y2="-1.0252e-05" stroke="#FF7B00" stroke-width="0.444444"></line>
                    <line x1="8.22222" y1="-5.77347e-09" x2="8.22222" y2="2.66667" stroke="#FF7B00" stroke-width="0.444444"></line>
                    <line x1="7.77778" y1="16" x2="7.77778" y2="13.3333" stroke="#FF7B00" stroke-width="0.444444"></line>
                    <line x1="8.22222" y1="13.3333" x2="8.22222" y2="16" stroke="#FF7B00" stroke-width="0.444444"></line>
                </svg>    
                <a href="https://yandex.ru/maps/?pt=${place.coord[0]},${place.coord[1]}&z=16&l=map" target="_blank">
                    ${place.coord[0]}, ${place.coord[1]}
              </a>
            </div>
          </div>
        </div>

        <div class="objDescriptionWrapper">
            <div class="objDescription truncatedText">
                ${place.description}
            </div>
        </div>
        <div class="ObjFooter" 
        data-text="
        ${place.reason}
        "
        >
          Почему мне предложили этот объект?
        </div>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
  });
}

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
