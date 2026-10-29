"""Print a header and one row for a region: its elevation range from its DEM
and its mean and steepest slope from its slope raster."""
import sys

from osgeo import gdal

gdal.UseExceptions()
# Statistics stay in memory, not in a .aux.xml beside the raster.
gdal.SetConfigOption("GDAL_PAM_ENABLED", "NO")
region, dem, slope = sys.argv[1:]


def stats(path):
    raster = gdal.Open(path)
    return raster.GetRasterBand(1).ComputeStatistics(False)  # minimum, maximum, mean, standard deviation


low, high, mean, _ = stats(dem)
_, steepest, mean_slope, _ = stats(slope)
print("region\tlowest_m\thighest_m\tmean_m\tmean_slope_deg\tsteepest_deg")
print(f"{region}\t{low:.0f}\t{high:.0f}\t{mean:.0f}\t{mean_slope:.1f}\t{steepest:.1f}")
