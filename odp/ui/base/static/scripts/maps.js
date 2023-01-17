function createExtentMap(n, e, s, w) {
    $('#map').height('300px');
    const map = L.map('map', {
        center: [(n + s) / 2, (e + w) / 2],
        zoom: 4,
        gestureHandling: true
    });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19
    }).addTo(map);
    L.control.scale({
        metric: true,
        imperial: false
    }).addTo(map);

    if (n === s && e === w) {
        const marker = L.marker([n, e], {}).addTo(map);
    } else {
        const bounds = [[n, e], [s, w]];
        const color = getComputedStyle(document.documentElement)
            .getPropertyValue('--bs-danger');
        L.rectangle(bounds, {
            color: color,
            weight: 1
        }).addTo(map);
        map.fitBounds(bounds, {
            animate: false,
            maxZoom: 9
        });
    }
}
