# notes

## catalogue structure

- Does each COG have to be an item?
  - that seems like it's a lot of overhead, if we have lots of COGs? maybe not... just a db record per cog

What kind of searches do we want
- give me all the AOI available for customer X
- give me the AOI for customer X, for SOC
- give me all the AOI available for all customers in CONUS where resolution is <= 30m
- give me all the public (demo) AOI for SOC
  - where resolution <=30m

If we can catalogue mosaics
- Give me SOCSPOT mosaic data which includes AOI geometry
- Give me sample points from customer X within AOI geometry


TODO: would be great to formalize these in planning doc
    make part of a workflow

    eg. for generating a L1 request for a customer, here's how workflow would interact with STAC
        for ingesting field boundaries ...
        for generating L2
        for ingesting customer sample data
        for generating L3 from customer sample data
        for displaying each of these things in the platform
            - field boundaries
            - sample points
            - tiles for generated data
            - vector for aggregated data
            - plots, etc for generated data


## Issues

Are bounds incorrect on SOC mosaic?
s3://perennial-internal-web-ready-artifacts/vesta/production/82d12c7a/prism_precip__30yr_historic__mean/mosaic.json

☝️mosaic used by terra for ATLAS-SOC basemap, as of terra 5657145ea

Appears to be a very small area, not conus
