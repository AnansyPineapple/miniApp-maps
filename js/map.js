ymaps.ready(init);

function init() {
    // Создаём карту
    const map = new ymaps.Map("map", {
        center: [56.326797, 44.006516], // Нижний Новгород
        zoom: 12,
        controls:[]
    });
    map.behaviors.disable(['scrollZoom', 'drag', 'dblClickZoom']);

    const routeData = JSON.parse(localStorage.getItem('routeData'));

    if (routeData && routeData.places && Array.isArray(routeData.places)) {
        //Добавляем стартовую точку
        ymaps.geocode(routeData.startPoint, {results: 1}).then(function (start_point) {
            const start_placemark = new ymaps.Placemark(
                start_point.geoObjects.get(0).geometry.getCoordinates(),
                {balloonContent: "Start Point"},
                {preset: "islands#redDotIcon" }
            );
            map.geoObjects.add(start_placemark);
        });

        //Добавляем остальные точки
        routeData.places.forEach((place, index) => {
            const placemark = new ymaps.Placemark(
                [place.coord[0], place.coord[1]],
                { balloonContent: place.title },
                { preset: "islands#orangeDotIcon" }
            );
            map.geoObjects.add(placemark);
        });
    }
}
