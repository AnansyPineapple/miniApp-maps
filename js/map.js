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
        const start_point = ymaps.geocode(routeData.startPoint, {results: 1})
            .then(function (start) {
                const start_coords = start.geoObjects.get(0).geometry.getCoordinates();

                const points = [start_coords];

                const start_placemark = new ymaps.Placemark(
                    start_coords,
                    {balloonContent: "Start Point"},
                    {preset: "islands#redDotIcon" }
                );
                map.geoObjects.add(start_placemark);

                //Добавляем остальные точки
                routeData.places.forEach((place, index) => {
                    const coords = [place.coord[1], place.coord[0]];
                    points.push(coords);

                    const placemark = new ymaps.Placemark(
                        coords,
                        { balloonContent: place.title },
                        { preset: "islands#orangeDotIcon" }
                    );        
                    map.geoObjects.add(placemark);
                });

                const multiRoute = new ymaps.multiRouter.MultiRoute({
                    referencePoints: points,
                },{
                    editorDrawOver: false,
                    routeStrokeColor: "000088",
                    routeActiveStrokeColor: "ff0000",
                    pinIconFillColor: "ff0000",
                    boundsAutoApply: true,
                    zoomMargin: 30
                });

                map.geoObjects.add(multiRoute);
        
                multiRoute.events.once('update', function() {
                    const routes = multiRoute.getRoutes();
                    for (let i = 0, l = routes.getLength(); i < l; i++) {
                        const route = routes.get(i);
                        if (!route.properties.get('blocked')) {
                            multiRoute.setActiveRoute(route);
                            route.balloon.open();
                            break;
                        }
                    }
                });
            });
    }
}
