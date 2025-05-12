# Lab 5 scripts

import importlib
import nc_lab5_functions as l5

importlib.reload(l5)


# ---------------------------------------------------
# Part 1: Create a SmartRaster and calculate NDVI
# ---------------------------------------------------

# Set path to Landsat image
landsat_path = "Landsat_image_corv.tif"

# Create SmartRaster object
sr = l5.SmartRaster(landsat_path)

# Call the NDVI calculator
# By default, uses Band 4 (NIR) and Band 3 (Red) and saves output
sr.calculate_ndvi(out_path="ndvi_output.tif")


# ---------------------------------------------------
# Part 2: Create a SmartVector and join zonal stats
# ---------------------------------------------------

# Set path to shapefile
parcels_path = "Benton_County_TaxLots.shp"

# Create a SmartVector object
sv = l5.SmartVector(parcels_path)

# Run zonal statistics to calculate average NDVI per parcel
# Adds a new column called "NDVI_mean" and uses the new NDVI raster
if sv.zonal_stats_to_field("ndvi_output.tif", field_name="NDVI_mean"):
    # Save the updated shapefile
    sv.save("Benton_County_TaxLots_with_ndvi.shp")


# ---------------------------------------------------
# Part 3: Optional Visualization
# ---------------------------------------------------

# This section uses matplotlib to make a simple NDVI map
import matplotlib.pyplot as plt

# Use the GeoDataFrame's built-in plot method to color polygons by NDVI
sv.gdf.plot(column="NDVI_mean", cmap="YlGn", legend=True, edgecolor="k")

# Add title and remove axes
plt.title("Average NDVI by Parcel")
plt.axis("off")
plt.show()
