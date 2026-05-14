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
        tiles='OpenStreetMap'
    )

    # Add a second tile layer option
    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)

    # Create a separate layer for knooppunten
    knooppunt_layer = folium.FeatureGroup(name='Fietsknooppunten', show=True)

    # Use MarkerCluster for performance (10k+ markers)
    marker_cluster = MarkerCluster().add_to(knooppunt_layer)

    for k in knooppunten:
        folium.CircleMarker(
            location=[k['lat'], k['lon']],
            radius=6,
            color='green',
            fill=True,
            fill_color='white',
            fill_opacity=0.9,
            weight=2,
            tooltip=f"Knooppunt {k['rcn_ref']}",
            popup=folium.Popup(
                f"<b>Knooppunt {k['rcn_ref']}</b><br>"
                f"Lat: {k['lat']:.5f}<br>"
                f"Lon: {k['lon']:.5f}",
                max_width=200
            )
        ).add_to(marker_cluster)

    knooppunt_layer.add_to(m)

    # Add layer control to toggle knooppunten on/off
    folium.LayerControl(collapsed=False).add_to(m)

    # Add a title
    title_html = '''
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                    z-index: 1000; background-color: white; padding: 10px 20px;
                    border-radius: 5px; border: 2px solid green;
                    font-size: 16px; font-weight: bold;">
            🚲 Fietsknooppunten Nederland
        </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    return m


if __name__ == '__main__':
    print("Loading knooppunten...")
    knooppunten = load_knooppunten('knooppunten.json')
    print(f"Loaded {len(knooppunten)} knooppunten")

    print("Creating map...")
    m = create_map(knooppunten)

    output_file = 'fietsknooppunten.html'
    m.save(output_file)
    print(f"Map saved to {output_file}")
    print("Open the file in your browser to view the interactive map.")