ymaps.ready(init);

function init() {
  const map = new ymaps.Map("map", {
    center: [56.326797, 44.006516],
    zoom: 12,
    controls: []
  });

  const routeData = JSON.parse(localStorage.getItem('routeData'));
  if (!routeData || !routeData.places) return;

  const coords = routeData.places.map(p => p.coord);

  coords.forEach(c => {
    map.geoObjects.add(new ymaps.Placemark(c, {}, {preset: "islands#orangeDotIcon"}));
  });

  if (coords.length > 1) {
    const route = new ymaps.Polyline(coords, {}, {strokeColor: "#FF7B00", strokeWidth: 3});
    map.geoObjects.add(route);
    map.setBounds(route.geometry.getBounds());
  }
}


