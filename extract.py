import json


def extract_knooppunten(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    knooppunten = []

    elements = data.get('elements', [])

    for element in elements:
        if (element.get('type') == 'node' and
                'tags' in element and
                'rcn_ref' in element['tags']):
            knooppunt = {
                'rcn_ref': element['tags']['rcn_ref'],
                'lat': element['lat'],
                'lon': element['lon']
            }
            knooppunten.append(knooppunt)

    return knooppunten


if __name__ == '__main__':
    knooppunten = extract_knooppunten('knooppunten.json')

    print(f"Found {len(knooppunten)} knooppunten\n")
    print(f"{'rcn_ref':<10} {'lat':<15} {'lon':<15}")
    print("-" * 40)
    for k in sorted(knooppunten, key=lambda x: x['rcn_ref'].zfill(3)):
        print(f"{k['rcn_ref']:<10} {k['lat']:<15} {k['lon']:<15}")