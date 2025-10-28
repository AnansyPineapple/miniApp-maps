ymaps.ready(init);

function init() {
    const map = new ymaps.Map("map", {
        center: [56.326797, 44.006516],
        zoom: 12,
        controls:[]
    });
    map.behaviors.disable(['scrollZoom', 'drag', 'dblClickZoom']);
    
    const places = loadPlacesData();
    
    if (places && places.length > 0) {
        map.setCenter([places[0].coordinates.lat, places[0].coordinates.lon]);
        
        places.forEach((place, index) => {
            const placemark = new ymaps.Placemark(
                [place.coordinates.lat, place.coordinates.lon],
                {
                    balloonContent: `<b>${index + 1}. ${place.title}</b><br>${place.address}`
                },
                {
                    preset: "islands#orangeDotIcon"
                }
            );
            
            map.geoObjects.add(placemark);
        });
    } else {
        const placemark = new ymaps.Placemark([56.326797, 44.006516], {
            balloonContent: "Центр Нижнего Новгорода"
        }, {
            preset: "islands#orangeDotIcon"
        });

        map.geoObjects.add(placemark);
    }
}

function loadPlacesData() {
    const urlParams = new URLSearchParams(window.location.search);
    const dataParam = urlParams.get('data');
    
    console.log('URL params:', window.location.search);
    console.log('Data param:', dataParam);

    if (dataParam) {
        try {
            const decodedData = decodeURIComponent(dataParam);
            return JSON.parse(decodedData);
        } catch (e) {
            console.error('Error parsing places data:', e);
            return [];
        }
    }

    const storedData = localStorage.getItem('formData');
    if (storedData) {
        console.log('Using stored data:', storedData);
    }
    
    return [];
}