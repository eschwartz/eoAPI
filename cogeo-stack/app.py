import datetime

from cogeo_mosaic.backends.stac import STACBackend, MosaicJSON
from flask import Flask, jsonify
import httpx
from rio_tiler.mosaic.methods import FirstMethod
from rio_tiler.colormap import cmap


app = Flask(__name__)

"""
NOTE
Was hoping cogeo-mosaic would fix issues I'm seeing with titiler and STAC,
that we're getting partially rendered tiles

But the STACBackend in cogeo-mosaic is for a much older version of stac-api
"""

@app.route('/tiles/<int:z>/<int:x>/<int:y>.png')
def get_tile(z, x, y):
    """
    url = "http://localhost:8081/collections/atlas-soc/items?limit=500"
    items = httpx.get(url).json()
    mosaic = MosaicJSON.from_features(
        items["features"],
        minzoom=3,
        maxzoom=12,
        accessor=lambda f: f["assets"]["cog"]["href"],
        colormap=cmap.get("viridis")
    )

    image, assets = mosaic.tile(x, y, z, pixel_selection=FirstMethod)



    return image
    """

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                30.810813903808594,
                                29.454247067148533
                            ],
                            [
                                30.88600158691406,
                                29.454247067148533
                            ],
                            [
                                30.88600158691406,
                                29.51879923863822
                            ],
                            [
                                30.810813903808594,
                                29.51879923863822
                            ],
                            [
                                30.810813903808594,
                                29.454247067148533
                            ]
                        ]
                    ]
                }
            }
        ]
    }

    date_min = "2019-01-01"
    date_max = "2019-12-11"

    start = datetime.datetime.strptime(date_min, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00Z")
    end = datetime.datetime.strptime(date_max, "%Y-%m-%d").strftime("%Y-%m-%dT23:59:59Z")

    query = {
        "collections": ["atlas-soc"],
        # "datetime": f"{start}/{end}",
        # "query": {
        #     "eo:cloud_cover": {
        #         "lt": 5
        #     }
        # },
        # "intersects": geojson["features"][0]["geometry"],
        "limit": 1000,
        # "fields": {
        #     'include': ['id', 'properties.datetime', 'properties.data_coverage'],
        #     'exclude': ['assets']
        # }
    }


    """
    NOTE: STACBackend expects context extension, which is deprecrated and removed from pgstac
    See https://github.com/stac-utils/stac-fastapi/issues/649
    
    Had to update _fetch in venv/lib/python3.11/site-packages/cogeo_mosaic/backends/stac.py
    to not use it.
    """

    with STACBackend(
            "http://localhost:8081/search",
            query=query,
            minzoom=8,
            maxzoom=15,
            colormap=cmap.get("viridis")
    ) as mosaic:
        print(mosaic.mosaic_def.dict(exclude={"tiles"}))
        image, assets = mosaic.tile(x, y, z, pixel_selection=FirstMethod, assets="cog")

        return image

if __name__ == '__main__':
    app.run(debug=True)
