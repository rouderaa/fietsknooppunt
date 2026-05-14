import json
import folium
from folium.plugins import MarkerCluster


def load_knooppunten(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    knooppunten = []
    for element in data.get('elements', []):
        if (element.get('type') == 'node' and
                'tags' in element and
                'rcn_ref' in element['tags']):
            knooppunten.append({
                'rcn_ref': element['tags']['rcn_ref'],
                'lat': element['lat'],
                'lon': element['lon']
            })
    return knooppunten


def create_map(knooppunten):
    # Center map on the Netherlands
    m = folium.Map(
        location=[52.3, 5.3],
        zoom_start=8,
        tiles='OpenStreetMap',
        control_scale=True
    )

    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)
    marker_cluster = MarkerCluster(name='Fietsknooppunten').add_to(m)

    # JavaScript logic for selection and GPX export
    # We use a slight delay to ensure 'map' is initialized by folium
    custom_js = """
    var selectedNodes = [];
    var polyline;

    function initRouteLogic() {
        if (typeof map !== 'undefined') {
            polyline = L.polyline([], {color: 'red', weight: 5, opacity: 0.8}).addTo(map);
        } else {
            setTimeout(initRouteLogic, 100);
        }
    }

    function addToRoute(name, lat, lon) {
        selectedNodes.push({name: name, lat: lat, lon: lon});
        updateUI();
        if (polyline) {
            var coords = selectedNodes.map(node => [node.lat, node.lon]);
            polyline.setLatLngs(coords);
        }
    }

    function updateUI() {
        var listDiv = document.getElementById('route-list');
        listDiv.innerHTML = selectedNodes.map((n, i) => 
            `<div style="padding: 2px 0; border-bottom: 1px solid #eee;">${i+1}. Punt ${n.name}</div>`
        ).join('');
    }

    function clearRoute() {
        selectedNodes = [];
        updateUI();
        if (polyline) polyline.setLatLngs([]);
    }

    function downloadGPX() {
        if (selectedNodes.length === 0) {
            alert("Selecteer eerst een paar knooppunten!");
            return;
        }

        let gpx = '<?xml version="1.0" encoding="UTF-8"?>\\n';
        gpx += '<gpx version="1.1" creator="Folium-Knooppunt-Planner" xmlns="http://www.topografix.com/GPX/1/1">\\n';
        gpx += '  <trk><name>Mijn Fietsroute</name><trkseg>\\n';

        selectedNodes.forEach(node => {
            gpx += `    <trkpt lat="${node.lat}" lon="${node.lon}"><name>${node.name}</name></trkpt>\\n`;
        });

        gpx += '  </trkseg></trk>\\n</gpx>';

        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/xml;charset=utf-8,' + encodeURIComponent(gpx));
        element.setAttribute('download', 'route.gpx');
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }

    initRouteLogic();
    """

    for k in knooppunten:
        # Create a cleaner popup with a styled button
        popup_content = f"""
            <div style="font-family: sans-serif; text-align: center;">
                <strong>Knooppunt {k['rcn_ref']}</strong><br><br>
                <button onclick="addToRoute('{k['rcn_ref']}', {k['lat']}, {k['lon']})" 
                        style="cursor:pointer; background-color: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 3px;">
                    Voeg toe
                </button>
            </div>
        """
        folium.CircleMarker(
            location=[k['lat'], k['lon']],
            radius=6,
            color='green',
            fill=True,
            fill_color='white',
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(popup_content, max_width=150)
        ).add_to(marker_cluster)

    # Injecting the JS
    m.get_root().script.add_child(folium.Element(custom_js))

    # Improved Sidebar and Title HTML with absolute positioning
    controls_html = '''
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                    z-index: 9999; background-color: rgba(255, 255, 255, 0.9); padding: 10px 20px;
                    border-radius: 8px; border: 2px solid green; font-family: sans-serif;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2); font-weight: bold;">
            🚲 Knooppunt Planner
        </div>

        <div style="position: fixed; top: 80px; right: 10px; width: 180px; 
                    z-index: 9999; background-color: white; padding: 15px;
                    border-radius: 8px; border: 1px solid #ccc; font-family: sans-serif;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #4CAF50;">Jouw Route</h4>
            <div id="route-list" style="max-height: 250px; overflow-y: auto; margin-bottom: 15px; font-size: 13px; color: #333;">
                <i style="color: #888;">Nog geen punten geselecteerd...</i>
            </div>
            <button onclick="downloadGPX()" style="width:100%; margin-bottom:8px; cursor:pointer; background:#2196F3; color:white; border:none; padding:8px; border-radius:4px;">Download GPX</button>
            <button onclick="clearRoute()" style="width:100%; cursor:pointer; background:#f44336; color:white; border:none; padding:8px; border-radius:4px;">Wis Route</button>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(controls_html))

    return m


if __name__ == '__main__':
    try:
        print("Loading data...")
        nodes = load_knooppunten('knooppunten.json')
        print(f"Loaded {len(nodes)} points. Generating map...")

        map_obj = create_map(nodes)
        map_obj.save('planner.html')
        print("Done! Open 'planner.html' in your browser.")
    except Exception as e:
        print(f"An error occurred: {e}")