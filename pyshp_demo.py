import shapefile
import json
import logging

logging.basicConfig(level=logging.INFO)

def features(data, filter=None):
    """	Reads a given shapefile and returns its features (records) in geoJSON-like format.
    If a filter is given, all fields not included in the filter will be dropped from output.
    data: path to shapefile
    filter: list of specific field names to include (default None)
    """

    sf = shapefile.Reader(data)
    fields = sf.fields[1:] # sf.fields[0] == deletion flag
    field_names = [field[0] for field in fields]

# TODO
# validate geometries - dump bad/null geoms
# some null geometries still return [invalid] coords - not (0,0)

    for r in sf.shapeRecords():
        coords = r.shape.__geo_interface__['coordinates']
        logging.debug("%r %r", type(coords), coords)
        if coords == (0,0):
            continue
        else:
            all_attr = dict(zip(field_names, r.record))
            if filter:
                attr = {field: all_attr[field] for field in filter}
            else:
                attr = all_attr
            geom = r.shape.__geo_interface__

            yield dict(type="Feature", geometry=geom,properties=attr)


if __name__ == "__main__":
    shp = "data/gazetteer"
    filter_fields = ["NAME", "CLASS"]
    museums = []

    spatial_records = features(shp, filter_fields)
    for rec in spatial_records:
        # filter out only features that show museum locations
        if rec['properties']['CLASS'].lower() == "museum":
            museums.append(rec)

    geojsonized = dict(type="FeatureCollection", features=museums)
    with open("museums.json", "w") as f:
        f.write(json.dumps(geojsonized))
