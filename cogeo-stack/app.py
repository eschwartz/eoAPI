import datetime
from typing import Tuple

from cogeo_mosaic.backends.stac import STACBackend
from flask import Flask
from rio_tiler.colormap import cmap
from rio_tiler.models import ImageData
from rio_tiler.mosaic.methods import FirstMethod
from rio_tiler.utils import linear_rescale
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

"""
NOTE
Was hoping cogeo-mosaic would fix issues I'm seeing with titiler and STAC,
that we're getting partially rendered tiles

But it doesn't.

It's also a little broken, because STACBackend expects context extension, which is deprecrated and removed from pgstac
See https://github.com/stac-utils/stac-fastapi/issues/649

Had to update _fetch in venv/lib/python3.11/site-packages/cogeo_mosaic/backends/stac.py
to not use it. 

Now it's working, but the tiles have the same issues as I'm seeing in titiler
Maybe we need to generate the COGS different, or there some metadata we're missing?
"""


class ColorMapService:
    def __init__(
            self,
            colormap_name: str,
            use_interval_colormap: bool,
            min_value: float,
            max_value: float,
    ):
        self.colormap_name = colormap_name
        self.use_interval_colormap = use_interval_colormap
        self.min_value = min_value
        self.max_value = max_value

    def _get_colormap(self):
        return cmap.get(self.colormap_name)

    def _colormap_keys(self):
        colormap = self._get_colormap()
        all_values = list(colormap.keys())
        min_value = min(colormap.keys())
        max_value = max(colormap.keys())
        return all_values, min_value, max_value

    def get_colormap(self):
        colormap = self._get_colormap()
        return colormap

    def rescaled_colormap(self) -> list[Tuple[int, list]]:
        colormap = self._get_colormap()
        cm_all_values, cm_min_value, cm_max_value = self._colormap_keys()
        rescaled_values = linear_rescale(
            cm_all_values,
            in_range=(cm_min_value, cm_max_value),
            out_range=(self.min_value, self.max_value),
        )
        return [
            (rescaled_value, list(map(int, colormap[cm_all_values[idx]])))
            for idx, rescaled_value in enumerate(rescaled_values)
        ]

    def render(self, image: ImageData):
        _, cm_min_value, cm_max_value = self._colormap_keys()
        colormap = self.get_colormap()
        image.rescale(
            in_range=((self.min_value, self.max_value),),
            out_range=((cm_min_value, cm_max_value),),
        )
        return image.render(colormap=colormap)


@app.route('/tiles/<int:z>/<int:x>/<int:y>.png')
def get_tile(z, x, y):

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


    cmap_svc = ColorMapService(colormap_name="viridis", min_value=0.19, max_value=5.12, use_interval_colormap=False)

    with STACBackend(
            "http://localhost:8081/search",
            query=query,
            minzoom=8,
            maxzoom=15
    ) as mosaic:
        print(mosaic.mosaic_def.dict(exclude={"tiles"}))
        image, assets = mosaic.tile(x, y, z, pixel_selection=FirstMethod, assets="cog")
        content = cmap_svc.render(image)
        return content

if __name__ == '__main__':
    app.run(debug=True)
