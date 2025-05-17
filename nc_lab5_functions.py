#####################
# Block 1:  Import packages

import os
import rasterio
import geopandas as gpd
import numpy as np
from rasterio import open as rio_open
from rasterstats import zonal_stats


##################
# Block 2: Set the working directory

data_dir = "R:\2025\Spring\GEOG562\Students\cramerni\Lab5_nc\lab5_code"
os.chdir(data_dir)
print(os.getcwd())


##################
# Block 3: New SmartRaster class using rasterio (with method "calculate_ndvi")

class SmartRaster:
    def __init__(self, filepath=None, array=None, meta=None, transform=None):
        """
        Initialize either from a file or from a NumPy array with metadata.
        """
        if filepath:
            with rasterio.open(filepath) as src:
                self.array = src.read()               # Load all bands into memory
                self.meta = src.meta.copy()           # Save metadata for saving later
                self.transform = src.transform        # Save the spatial transform
        elif array is not None and meta is not None:
            self.array = array
            self.meta = meta
            self.transform = transform or meta.get("transform")
        else:
            raise ValueError("You must provide either a filepath or an array + metadata.")

    def read(self, band=1):
        """
        Read a single band from the array (1-based index).
        """
        if self.array.ndim == 3:
            return self.array[band - 1]
        elif self.array.ndim == 2:
            return self.array
        else:
            raise ValueError("Invalid raster shape.")

    def compute_ndvi(self, nir_band=4, red_band=3):
        """
        Calculate NDVI from NIR and Red bands.
        Returns a new SmartRaster object with the NDVI array.
        """
        nir = self.read(nir_band).astype("float32")
        red = self.read(red_band).astype("float32")
        ndvi = (nir - red) / (nir + red + 1e-5)  # Add small value to avoid division by zero

        # Update metadata for single-band NDVI output
        ndvi_meta = self.meta.copy()
        ndvi_meta.update({
            "count": 1,
            "dtype": "float32"
        })

        return SmartRaster(array=ndvi, meta=ndvi_meta, transform=self.transform)

    def save(self, output_path):
        """
        Save the raster to a .tif file.
        """
        with rasterio.open(output_path, 'w', **self.meta) as dst:
            if self.array.ndim == 2:
                dst.write(self.array, 1)
            else:
                dst.write(self.array)

    def shape(self):
        return self.array.shape

    def __repr__(self):
        return f"<SmartRaster shape={self.shape()}, dtype={self.array.dtype}>"


##################
# Block 4: New SmartVector class using geopandas (to calculate zonal statistics)

class SmartVector(gpd.GeoDataFrame):
    def __init__(self, data=None, **kwargs):
        """
        Initialize from a file path, GeoDataFrame, or dict.
        """
        if isinstance(data, str) and os.path.exists(data):
            gdf = gpd.read_file(data)
            super().__init__(gdf.drop(columns=gdf.geometry.name),
                             geometry=gdf.geometry, crs=gdf.crs, **kwargs)
        elif isinstance(data, gpd.GeoDataFrame):
            super().__init__(data, **kwargs)
        else:
            super().__init__(data, **kwargs)

    @property
    def _constructor(self):
        return SmartVector

    def add_zonal_stat_from_raster(self, raster_path, stat='mean', new_column='zonal_stat'):
        """
        Compute a zonal statistic (e.g., mean NDVI) from a raster and add to the table.
        """
        with rio_open(raster_path) as src:
            raster_crs = src.crs
            nodata_val = src.nodata

        # Reproject geometries to match raster CRS if needed
        if isinstance(self.crs, dict) and 'init' in self.crs:
            self.crs = f"EPSG:{self.crs['init'].split(':')[1]}"
        gdf_proj = self.to_crs(raster_crs) if self.crs != raster_crs else self

        # Compute the zonal statistics
        stats = zonal_stats(
            vectors=gdf_proj,
            raster=raster_path,
            stats=[stat],
            nodata=nodata_val,
            geojson_out=False
        )

        # Add the results to a new column
        gdf_proj[new_column] = [item[stat] for item in stats]
        return self._constructor(gdf_proj)

    def save(self, output_path, driver=None, layer=None):
        """
        Save the vector data to disk (.shp or .gpkg).
        """
        if driver is None:
            if output_path.endswith(".gpkg"):
                driver = "GPKG"
            elif output_path.endswith(".shp"):
                driver = "ESRI Shapefile"
            else:
                raise ValueError("Please specify the driver for the given file type.")

        if driver == "GPKG" and layer:
            self.to_file(output_path, driver=driver, layer=layer)
        else:
            self.to_file(output_path, driver=driver)

    def __repr__(self):
        return f"<SmartVector shape={self.shape}, crs={self.crs}>"