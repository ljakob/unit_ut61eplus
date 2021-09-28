# small helper to convert JSON file
import json
import pprint

units = {}

with open('from_vendor/funOl_UT61E+.json') as src:
    data = json.load(src)
    print(data)
    for mode, d in data['OL'].items():
        units[mode] = {}
        for range, r in d.items():
            units[mode][range] = r[1]
    
print()
pprint.pprint(units)
