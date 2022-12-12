from desc.skycatalogs import skyCatalogs

# Simulation region: 51 < ra < 56, -42 < dec < -38
vertices = [(51, -42), (51, -38), (56, -38), (56, -42)]

region = skyCatalogs.PolygonalRegion(vertices)

sky_cat = skyCatalogs.open_catalog(
    '/global/cfs/cdirs/descssim/imSim/skyCatalogs/skyCatalog.yaml')

hps = sky_cat.get_hps_by_region(region)

print(hps)
