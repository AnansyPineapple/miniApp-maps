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
        const points = [];
        let promises = [];

        //Добавляем стартовую точку
        const start_point = map.geocode(routeData.startPoint, {results: 1})
            .then(function (start) {
                const coords = start.geoObjects.get(0).geometry.getCoordinates();
                points.unshift(coords);

                const start_placemark = new ymaps.Placemark(
                    coords,
                    {balloonContent: "Start Point"},
                    {preset: "islands#redDotIcon" }
                );
                map.geoObjects.add(start_placemark);
            });
        promises.push(start_point);

        //Добавляем остальные точки
        routeData.places.forEach((place, index) => {
            const coords = [place.coord[0], place.coord[1]];
            points.push(coords);

            const placemark = new ymaps.Placemark(
                coords,
                { balloonContent: place.title },
                { preset: "islands#orangeDotIcon" }
            );        
            map.geoObjects.add(placemark);
        });

        Promise.all(promises).then(() => {
            const multiRoute = ymaps.multiRouter.MultiRoute({
                referencePoints: points,
            },{
                editorDrawOver: false,
                wayPointDraggable: true,
                viaPointDraggable: true,
                routeStrokeColor: "000088",
                routeActiveStrokeColor: "ff0000",
                pinIconFillColor: "ff0000",
                boundsAutoApply: true,
                zoomMargin: 30
            });

            map.geoObjects.add(multiRoute);

            multiRoute.event.once('update', function() {
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
