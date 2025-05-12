# Lab 5 scripts

import importlib
import nc_lab5_functions as l5

importlib.reload(l5)


# PART 1: Smart Raster NDVI
landsat_path = "Landsat_image_corv.tif"
sr = l5.SmartRaster(landsat_path)

# Calculate NDVI and save output
sr.calculate_ndvi(out_path="ndvi_output.tif")


# PART 2: Smart Vector Zonal Stats
taxlots_path = "Benton_County_TaxLots.shp"
sv = l5.SmartVector(taxlots_path)

# Calculate zonal stats and attach NDVI to parcels
if sv.zonal_stats_to_field("ndvi_output.tif", field_name="NDVI_mean"):
    sv.save("Benton_TaxLots_with_ndvi.shp")


# PART 3: Optional Visualization
import matplotlib.pyplot as plt

sv.gdf.plot(column="NDVI_mean", cmap="YlGn", legend=True, edgecolor="k")
plt.title("Average NDVI by Tax Lot")
plt.axis("off")
plt.show()
