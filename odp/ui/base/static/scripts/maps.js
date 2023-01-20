function createExtentMap(n, e, s, w) {
    $('#map').height('300px');
    const map = _initMap(n, e, s, w);

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

function createFilterMap(n, e, s, w) {
    $('#map').height('300px');
    const map = _initMap(n, e, s, w, true);

    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    var drawControl = new L.Control.Draw({
        draw: {
            polyline: false,
            polygon: false,
            marker: false,
            circle: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems
        }
    });
    map.addControl(drawControl);
    map.on(L.Draw.Event.CREATED, function (event) {
        var layer = event.layer;
        drawnItems.addLayer(layer);
    });
}

function _initMap(n, e, s, w) {
    let lat = -33;
    let lon = 23;
    if (n && e && s && w) {
        lat = (n + s) / 2;
        lon = (e + w) / 2;
    }
    const map = L.map('map', {
        center: [lat, lon],
        zoom: 3,
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

    return map;
}
