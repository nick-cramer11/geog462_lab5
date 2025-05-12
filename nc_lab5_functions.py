#####################
# Block 1:  Import the packages you'll need
# 
# 

import os, sys
import rasterio
import geopandas as gpd
import numpy as np
from rasterstats import zonal_stats


##################
# Block 2: 
# set the working directory to the directory where the data are

# Change this to the directory where your data are

data_dir = "R:/2025/Spring/GEOG562/Students/cramerni/Lab5_nc/lab5_code"
os.chdir(data_dir)
print(f"Working directory set to: {os.getcwd()}")


##################
# Block 3: 
#   Set up a new smart raster class using rasterio  
#    that will have a method called "calculate_ndvi"

class SmartRaster:
    def __init__(self, raster_path):
        self.raster_path = raster_path
        self.ds = rasterio.open(raster_path)
        self.meta = self.ds.meta
        self.bounds = self.ds.bounds

    def calculate_ndvi(self, band4_index=4, band3_index=3, out_path="ndvi_output.tif"):
        try:
            nir = self.ds.read(band4_index).astype('float32')
            red = self.ds.read(band3_index).astype('float32')
            ndvi = (nir - red) / (nir + red + 1e-10)  # Prevent divide-by-zero

            # Save NDVI as a GeoTIFF
            meta = self.meta.copy()
            meta.update(dtype='float32', count=1)

            with rasterio.open(out_path, 'w', **meta) as dst:
                dst.write(ndvi, 1)

            print(f"NDVI written to {out_path}")
            return True
        except Exception as e:
            print(f"NDVI calculation error: {e}")
            return False


##################
# Block 4: 
#   Set up a new smart vector class using geopandas
#    that will have a method similar to what did in lab 4
#    to calculate the zonal statistics for a raster
#    and add them as a column to the attribute table of the vector

class SmartVector:
    def __init__(self, vector_path):
        self.gdf = gpd.read_file(vector_path)
        self.vector_path = vector_path

    def zonal_stats_to_field(self, raster_path, stat="mean", field_name="NDVI_mean"):
        try:
            stats = zonal_stats(self.gdf, raster_path, stats=stat, geojson_out=True)
            values = [f["properties"][stat] for f in stats]
            self.gdf[field_name] = values
            print(f"{field_name} added to GeoDataFrame")
            return True
        except Exception as e:
            print(f"Zonal stats error: {e}")
            return False

    def save(self, out_path):
        self.gdf.to_file(out_path)
        print(f"GeoDataFrame saved to {out_path}")