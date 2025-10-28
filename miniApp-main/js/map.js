ymaps.ready(init);

function init() {
    // Создаём карту
    const map = new ymaps.Map("map", {
        center: [56.326797, 44.006516], // Нижний Новгород
        zoom: 12,
        controls:[]
    });
    map.behaviors.disable(['scrollZoom', 'drag', 'dblClickZoom']);
    // Пример: добавление одной метки (можно заменить данными с бэкенда)
    const placemark = new ymaps.Placemark([56.326797, 44.006516], {
        balloonContent: "Центр Нижнего Новгорода"
    }, {
        preset: "islands#orangeDotIcon"
    });

    map.geoObjects.add(placemark);
}


