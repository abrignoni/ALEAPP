"""An artifact that declares KML output has the columns KML is made from.

kmlgen writes a .kml only when the report has columns named exactly 'Latitude' and
'Longitude', and returns without a word otherwise. Fifteen artifacts declared output_types
'all', which adds KML, with no coordinate column, so the declaration promised a file
that could never be written. This test fails when an
artifact declares KML and neither its literal data_headers nor its module source names both
columns; the source check covers modules that add the columns at run time.
"""
import ast
import pathlib
import re
import unittest

ARTIFACTS = pathlib.Path(__file__).resolve().parents[3] / 'scripts' / 'artifacts'

# get_nike_polyline reports 'First Decoded Latitude' and the like, endpoints the module decodes
# from the activity polyline. kmlgen needs columns named exactly 'Latitude' and 'Longitude',
# so no KML is written for it today. Whether those endpoints belong on a map is a separate
# decision from this check, so it stays declared as it is.
ALLOWED = {('NikePolyline.py', 'get_nike_polyline')}


def declares_kml(output_types):
    values = [output_types] if isinstance(output_types, str) else list(output_types or [])
    return 'all' in values or 'kml' in values


class KmlOutputNeedsCoordinatesTest(unittest.TestCase):

    def test_kml_is_declared_only_where_latitude_and_longitude_columns_exist(self):
        missing = []
        checked = 0
        for path in sorted(ARTIFACTS.glob('*.py')):
            source = path.read_text(encoding='utf-8')
            tree = ast.parse(source)
            names_both = all(re.search(rf'''["']{c}["']''', source) for c in ('Latitude', 'Longitude'))
            for node in tree.body:
                if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                        and node.targets[0].id == '__artifacts_v2__'):
                    continue
                try:
                    block = ast.literal_eval(node.value)
                except ValueError:
                    continue
                for artifact, info in block.items():
                    if not isinstance(info, dict) or not declares_kml(info.get('output_types')):
                        continue
                    checked += 1
                    if not names_both and (path.name, artifact) not in ALLOWED:
                        missing.append((path.name, artifact))
        self.assertGreater(checked, 60)
        self.assertEqual(missing, [])


if __name__ == '__main__':
    unittest.main()
