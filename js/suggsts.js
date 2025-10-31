ymaps.ready(init);

function init() {
    const suggest = new ymaps.SuggestView('thirdQuestion', {
        boundedBy: [
            [56.2, 43.8],
            [56.5, 44.1]
        ],
        strictBounds: true
    });
    
    suggest.events.add('suggest', function(e) {
        const data = e.get('suggestions');
        const container = document.getElementById('suggestionsContainer');
        container.innerHTML = '';
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = item.displayName;
            container.appendChild(div);
        });
    });
}
