# Lab 5 scripts

import os
import importlib
import matplotlib.pyplot as plt
import nc_lab5_functions as l5
importlib.reload(l5)  # Refresh functions in case the file has been updated

# Data directory
data_dir = r"R:\2025\Spring\GEOG562\Students\cramerni\Lab5_nc\lab5_code"
landsat_file = os.path.join(data_dir, "Landsat_image_corv.tif")  # Input Landsat image
parcels_file = os.path.join(data_dir, "Benton_County_TaxLots.shp")  # Input parcels shapefile
ndvi_output_file = os.path.join(data_dir, "ndvi_corv_output.tif")  # Output NDVI raster file


#  Part 1: Compute NDVI

landsat = l5.SmartRaster(landsat_file)  # Load raster using SmartRaster class
ndvi_raster = landsat.compute_ndvi()  # Compute NDVI using bands 4 and 3
if ndvi_raster:
    ndvi_raster.save(ndvi_output_file)  # Save the NDVI raster to disk
    print("NDVI saved successfully.")
else:
    print("NDVI computation failed.")

# Visualize NDVI
    
from rasterio import open as rio_open
with rio_open(ndvi_output_file) as src:
    ndvi_array = src.read(1)  # Read the NDVI raster as a NumPy array

# Display NDVI using matplotlib
plt.imshow(ndvi_array, cmap='RdYlGn', vmin=0, vmax=1)
plt.colorbar(label='NDVI')
plt.title('NDVI Image')
plt.xlabel('Column')
plt.ylabel('Row')
plt.tight_layout()
plt.show()



# Part 2: Zonal Statistics

parcels = l5.SmartVector(parcels_file)  # Load parcels using SmartVector class
parcels = parcels.add_zonal_stat_from_raster(ndvi_output_file, stat='mean', new_column='ndvi_mean')



#  Part 3: Optional Visualization

fig, ax = plt.subplots(figsize=(10, 8))
parcels.plot(
    column='ndvi_mean',            # Color polygons by NDVI mean
    cmap='Greens',                 # Green color scale
    legend=True,                   # Add legend
    edgecolor='black',            # Outline polygons
    linewidth=0.3,                # Thin boundary lines
    ax=ax
)
ax.set_title("Zonal Mean NDVI by Parcel", fontsize=14)
ax.set_axis_off()  # Hide axis
plt.tight_layout()
plt.show()
