// the user-drawn box on the filter-by-location map
let box;
const boxColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--bs-info');

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
        gestureHandling: true,
        gestureHandlingOptions: {
            duration: 1500
        }
    });
    L.tileLayer.provider(
        'Esri.WorldStreetMap'
    ).addTo(map);
    L.control.scale({
        metric: true,
        imperial: false
    }).addTo(map);

    return map;
}

function createExtentMap(n, e, s, w) {
    $('#map').height('300px');
    const map = _initMap(n, e, s, w);

    if (n === s && e === w) {
        L.marker([n, e]).addTo(map);
    } else {
        const bounds = [[n, e], [s, w]];
        L.rectangle(bounds, {
            color: boxColor
        }).addTo(map);
        map.fitBounds(bounds, {
            animate: false,
            maxZoom: 9
        });
    }
}

function createFilterMap() {
    $('#map').height('300px');

    const n = parseFloat($('#n').val());
    const e = parseFloat($('#e').val());
    const s = parseFloat($('#s').val());
    const w = parseFloat($('#w').val());
    const map = _initMap(n, e, s, w);

    const drawnItems = new L.FeatureGroup();
    const drawControl = new L.Control.Draw({
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
    map.addLayer(drawnItems);
    map.addControl(drawControl);

    if (n && e && s && w) {
        const bounds = [[n, e], [s, w]];
        box = L.rectangle(bounds, {
            color: boxColor
        });
        drawnItems.addLayer(box);
        map.fitBounds(bounds, {
            animate: false,
            maxZoom: 9
        });
    }

    map.on(L.Draw.Event.CREATED, function (event) {
        box = event.layer;
        drawnItems.addLayer(box);
    });

    map.on(L.Draw.Event.DELETED, function (event) {
        box = null;
    });
}

function initFilteredSearchProxy() {
    $('#q-proxy').keydown(function (e) {
        if (e.which === 13) {
            $('#q-proxy-btn').click();
        }
    });
}

function execFilteredSearchProxy() {
    var q = $('#q-proxy').val();
    $('#q').val(q);
    $('#apply-filter').click();
}

function setFilter() {
    if (box) {
        const bounds = box.getBounds();
        $('#n').val(bounds.getNorth());
        $('#e').val(bounds.getEast());
        $('#s').val(bounds.getSouth());
        $('#w').val(bounds.getWest());
    } else {
        $('#n').val('');
        $('#e').val('');
        $('#s').val('');
        $('#w').val('');
    }
}

function clearFilter() {
    $('#n').val('');
    $('#e').val('');
    $('#s').val('');
    $('#w').val('');
    $('#after').val('');
    $('#before').val('');
    $('#exclusive_region').val('');
    $('#exclusive_interval').val('');
}

function initCitation(defaultStyle) {
    const style = localStorage.getItem('citation-style');
    $('#citation-style').val(style || defaultStyle);
}

function formatCitation(doi) {
    const style = $('#citation-style').val();
    $.ajax({
        url: `https://doi.org/${doi}`,
        dataType: 'text',
        headers: {
            Accept: `text/x-bibliography; locale=en-GB; style=${style}`
        },
        success: function (result) {
            $('#citation').html(result);
            localStorage.setItem('citation-style', style);
        }
    });
}

function copyCitation() {
    const text = $('#citation').text();
    navigator.clipboard.writeText(text).then(function () {
        const tooltip = new bootstrap.Tooltip($('#copy-citation-btn'), {
            title: 'Copied!',
            trigger: 'manual'
        });
        tooltip.show();
        setTimeout(function () {
            tooltip.hide();
        }, 3000);
    });
}
