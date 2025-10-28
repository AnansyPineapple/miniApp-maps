ymaps.ready(init);

function init() {
    new ymaps.SuggestView('thirdQuestion', {
        boundedBy: [
            [56.2, 43.8], // юго-запад
            [56.5, 44.1]  // северо-восток
        ],
        strictBounds: true
    });
}