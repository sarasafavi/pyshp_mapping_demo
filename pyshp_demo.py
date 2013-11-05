import shapefile
import json

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
# gen1: yield records from Reader
# gen2: yields only valid (__geo_interface__['coordinates'] != (0,0) ) recs
# gen3: yields dict of specified attrs

    for r in sf.shapeRecords():
        if r.shape.__geo_interface__['coordinates'] == (0,0):
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
    shp = "data/TX_Gazetteer"
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
