# --------------------------
# Block 1: Import required libraries
import os, sys                      # For file system operations
import rasterio                     # For working with raster (image) data
import geopandas as gpd             # For vector data like shapefiles
import numpy as np                  # For numeric calculations (used for NDVI)
from rasterstats import zonal_stats # To calculate zonal statistics

# --------------------------
# Block 2: Set the working directory
data_dir = "R:/2025/Spring/GEOG562/Students/cramerni/Lab5_nc/lab5_code"
os.chdir(data_dir)
print(f"Working directory set to: {os.getcwd()}")


# --------------------------
# Block 3: SmartRaster class using Rasterio
# This class loads a raster and calculates NDVI from two bands (NIR and Red)

class SmartRaster:
    def __init__(self, raster_path):
        self.raster_path = raster_path          # Store the file path
        self.ds = rasterio.open(raster_path)    # Open the raster file
        self.meta = self.ds.meta                # Get metadata (like size, type, CRS, etc.)
        self.bounds = self.ds.bounds            # Get spatial extent

    def calculate_ndvi(self, band4_index=4, band3_index=3, out_path="ndvi_output.tif"):
        """
        Calculate NDVI using NIR (Band 4) and Red (Band 3).
        Save result to a new raster file.
        """
        try:
            # Read the two bands and convert to float for math
            nir = self.ds.read(band4_index).astype('float32')
            red = self.ds.read(band3_index).astype('float32')

            # NDVI formula: (NIR - Red) / (NIR + Red)
            ndvi = (nir - red) / (nir + red + 1e-10)  # Add tiny number to avoid divide-by-zero

            # Copy metadata and update it for a single-band float output
            meta = self.meta.copy()
            meta.update(dtype='float32', count=1)

            # Write NDVI to a new raster file
            with rasterio.open(out_path, 'w', **meta) as dst:
                dst.write(ndvi, 1)

            print(f"NDVI written to {out_path}")
            return True  # Signal success
        except Exception as e:
            print(f"NDVI calculation error: {e}")
            return False  # Signal failure


# --------------------------
# Block 4: SmartVector class using GeoPandas
# This class loads a vector layer and calculates the average NDVI for each polygon

class SmartVector:
    def __init__(self, vector_path):
        self.gdf = gpd.read_file(vector_path)  # Load shapefile or GeoJSON into a GeoDataFrame
        self.vector_path = vector_path

    def zonal_stats_to_field(self, raster_path, stat="mean", field_name="NDVI_mean"):
        """
        Calculate a zonal statistic (e.g., mean NDVI) for each polygon.
        Save it as a new column in the GeoDataFrame.
        """
        try:
            # Calculate stats and return list of values
            stats = zonal_stats(self.gdf, raster_path, stats=stat, geojson_out=True)

            # Pull just the value (mean NDVI) from each feature
            values = [f["properties"][stat] for f in stats]

            # Add to a new column in the table
            self.gdf[field_name] = values
            print(f"{field_name} added to GeoDataFrame")
            return True
        except Exception as e:
            print(f"Zonal stats error: {e}")
            return False

    def save(self, out_path):
        """Save the modified vector data (with added NDVI column) to a new file."""
        self.gdf.to_file(out_path)
        print(f"GeoDataFrame saved to {out_path}")
