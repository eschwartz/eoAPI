import datetime
import json
import os
from os import path

import fsspec
import mercantile
import pystac
import rasterio
from pystac.extensions.projection import ProjectionExtension


def get_cog_bounds(cog_url):
    """Extracts the bounding box and geometry from a COG."""
    with rasterio.open(cog_url) as src:
        bounds = src.bounds  # (left, bottom, right, top)
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]

        # Convert bounds to GeoJSON polygon
        geometry = {
            "type": "Polygon",
            "coordinates": [[
                [bounds.left, bounds.bottom],
                [bounds.right, bounds.bottom],
                [bounds.right, bounds.top],
                [bounds.left, bounds.top],
                [bounds.left, bounds.bottom]
            ]]
        }

    return bbox, geometry


def quadkey_to_geometry(quadkey):
    """Convert a quadkey to a bounding box and GeoJSON geometry."""
    tile = mercantile.quadkey_to_tile(quadkey)
    bbox = list(mercantile.bounds(tile))  # [west, south, east, north]

    geometry = {
        "type": "Polygon",
        "coordinates": [[
            [bbox[0], bbox[1]],
            [bbox[2], bbox[1]],
            [bbox[2], bbox[3]],
            [bbox[0], bbox[3]],
            [bbox[0], bbox[1]]
        ]]
    }

    return bbox, geometry


def mosaic_to_collection(mosaic_file, out_path, resolution_meters):
    with fsspec.open(mosaic_file) as f:
        mosaic = json.load(f)

    mosaic_date = datetime.datetime.fromisoformat(mosaic.get("layers", {}).get("date") or "2024-10-15")
    collection = pystac.Collection(
        id="atlas-soc",
        description=mosaic["description"],
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent([mosaic["bounds"]]),
            temporal=pystac.TemporalExtent([[mosaic_date, mosaic_date]])
        )
    )

    i = 0
    for quadkey, assets in mosaic["tiles"].items():
        bbox, geometry = quadkey_to_geometry(quadkey)
        item = pystac.Item(
            id=quadkey,
            geometry=geometry,
            bbox=bbox,
            datetime=mosaic_date,
            properties={},
        )
        for asset_url in assets:
            item.add_asset(
                "cog",
                pystac.Asset(href=asset_url, media_type=pystac.MediaType.COG)
            )

            proj = ProjectionExtension.ext(item, add_if_missing=True)
            proj.epsg = 3857
            proj.resolution = [resolution_meters, resolution_meters]
        collection.add_item(item)

        i += 1
        if i % 10 == 0:
            print(f"{i} / {len(mosaic['tiles'])} tiles ingested")

    collection.normalize_and_save(out_path, pystac.CatalogType.SELF_CONTAINED)


mosaic_to_collection(
    # path.join(path.dirname(__file__), "soc.mosaic.json"),
    "s3://perennial-internal-web-ready-artifacts/vesta/production/82d12c7a/prism_precip__30yr_historic__mean/mosaic.json",
    out_path=path.join(os.getcwd(), "soc_stac_catalog"),
    resolution_meters=500
)
