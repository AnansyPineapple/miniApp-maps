ymaps.ready(init);

function init() {
    function calculateDistance(coord1, coord2) {
        return ymaps.coordSystem.geo.getDistance(coord1, coord2);
    }

    function formatDistance(distance) {
        if (distance < 1000) {
            return `${Math.round(distance)} м`;
        } 
        else {
            return `${(distance / 1000).toFixed(2)} км`;
        }
    }

    // Функция для расчета времени через маршрутизатор
    async function calculateRouteTime(startCoords, endCoords, transportType = 'auto') {
        return new Promise((resolve, reject) => {
            ymaps.route([
                startCoords,
                endCoords
            ], {
                routingMode: transportType
            }).then(
                function (route) {
                    const timeInSeconds = route.getJamsTime();
                    const timeInMinutes = Math.round(timeInSeconds / 60);
                    resolve(timeInMinutes);
                },
                function (error) {
                    console.error('Ошибка расчета маршрута:', error);
                    const distance = calculateDistance(startCoords, endCoords);
                    const approximateTime = Math.round(distance / 250); // ~250 м/мин = 15 км/ч
                    resolve(approximateTime);
                }
            );
        });
    }

    // Функция для форматирования времени
    function formatTime(minutes) {
        if (minutes < 60) {
            return `${minutes} мин.`;
        } else {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return mins > 0 ? `${hours}ч. ${mins}мин.` : `${hours}ч.`;
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('active');
        }
    });

    const routeData = JSON.parse(localStorage.getItem('routeData'));
    console.log('Received data:', routeData);
    
    if (routeData && routeData.places && Array.isArray(routeData.places)) {
        const container = document.querySelector('.ansContainer');

        const Time = routeData.totalTime;
        const Hours = routeData.hours;
        const Minutes = routeData.minutes;
        
        ymaps.geocode(routeData.startPoint, {results: 1})
            .then(async function (start) {
                const start_coords = start.geoObjects.get(0).geometry.getCoordinates();
                
                // Сортируем места по расстоянию от стартовой точки
                routeData.places.sort((a, b) => {
                    const distA = calculateDistance(start_coords, [a.coord[0], a.coord[1]]);
                    const distB = calculateDistance(start_coords, [b.coord[0], b.coord[1]]);
                    return distA - distB;
                });

                // Рассчитываем время для каждого отрезка маршрута
                for (let index = 0; index < routeData.places.length; index++) {
                    const place = routeData.places[index];
                    let distance = 0;
                    let distanceText = "0 м";
                    let travelTime = 0;
                    let travelTimeText = "0 мин.";

                    if (index === 0) {
                        // От стартовой точки до первого объекта
                        distance = calculateDistance(
                            [start_coords[0], start_coords[1]],
                            [place.coord[0], place.coord[1]]
                        );
                        distanceText = formatDistance(distance);
                        travelTime = await calculateRouteTime(start_coords, place.coord);
                        travelTimeText = formatTime(travelTime);
                    } 
                    else {
                        // От предыдущего объекта до текущего
                        const prevPlace = routeData.places[index - 1];
                        distance = calculateDistance(
                            [prevPlace.coord[0], prevPlace.coord[1]],
                            [place.coord[0], place.coord[1]]
                        );
                        distanceText = formatDistance(distance);
                        travelTime = await calculateRouteTime(prevPlace.coord, place.coord);
                        travelTimeText = formatTime(travelTime);
                    }

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

                            <div class="TimeToObj">
                                <div class="timeToObjText">
                                    Расстояние до объекта от предыдущей точки:
                                </div>
                                <div class="number">${distanceText}</div>
                            </div>
                            
                            <div class="TimeToObj">
                                <div class="timeToObjText">
                                    Время в пути:
                                </div>
                                <div class="number">${travelTimeText}</div>
                            </div>
                            
                            <div class="TimeToObj">
                                <div class="timeToObjText">
                                    Время на объекте:
                                </div>
                                <div class="number">${place.time} минут</div>
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
                }

                const finalReport = `
                    <div class="finalReport aboutObject">
                        <div class="reportTitle">   
                            Информация о маршруте:
                        </div>
                        <div class="reportCont">
                            <div class="inputedTime">
                                <div class="inputedTimeText">
                                    Введенное время:
                                </div>
                                <div class="number">${routeData.enteredTime || Time}</div>
                            </div>
                            <div class="realTime">
                                <div class="inputedTimeText">
                                    Предложенный маршрут:
                                </div>
                                <div class="number">${routeData.totalTime}</div>
                            </div>
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', finalReport);

                // Скрываем прелоадер после загрузки всех данных
                const overlay = document.getElementById('loadingOverlay');
                if (overlay) {
                    overlay.classList.remove('active');
                }
            })
            .catch(function (error) {
                console.error('Ошибка геокодирования:', error);
                // Скрываем прелоадер в случае ошибки
                const overlay = document.getElementById('loadingOverlay');
                if (overlay) {
                    overlay.classList.remove('active');
                }
            });
    }

    // Остальной код (модальные окна, копирование и т.д.) остается без изменений
    const modalOverlay = document.getElementById('modalOverlay');
    const modalText = document.querySelector('.modalText');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    document.querySelectorAll('.ObjFooter').forEach(el => {
        el.addEventListener('click', () => {
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

    // Ставит индексы у объектов
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
        window.location.href = 'form.html';
    });

    window.addEventListener('load', () => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            setTimeout(() => {
                overlay.classList.remove('active');
            }, 350); 
        }
    });
}
