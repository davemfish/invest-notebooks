import math
import os

import geometamaker
import numpy
import pygeoprocessing
import matplotlib.pyplot as plt
import marimo as mo
import pandas
import yaml
from osgeo import gdal

params = {
    'legend.fontsize': 'small',
    # 'figure.figsize': (15, 5),
    # 'axes.labelsize': 'x-large',
    'axes.titlesize': 'small',
    'xtick.labelsize': 'small',
    'ytick.labelsize': 'small'
    }
plt.rcParams.update(params)


def read_masked_array(filepath, resample_method):
    info = pygeoprocessing.get_raster_info(filepath)
    nodata = info['nodata'][0]
    resampled = False
    if os.path.getsize(filepath) > 4e6:
        resampled = True
        raster = gdal.OpenEx(filepath)
        band = raster.GetRasterBand(1)
        if band.GetOverviewCount() == 0:
            pygeoprocessing.build_overviews(
                filepath,
                internal=False,
                resample_method=resample_method,
                overwrite=False, levels='auto')

        raster = gdal.OpenEx(filepath)
        band = raster.GetRasterBand(1)
        n = band.GetOverviewCount()
        array = band.GetOverview(n - 1).ReadAsArray()
        raster = band = None
    else:
        array = pygeoprocessing.raster_to_numpy_array(filepath)
    masked_array = numpy.where(array == nodata, numpy.nan, array)
    return (masked_array, resampled)


COLORMAPS = {
    'continuous': 'viridis',
    'nominal': 'Set3',
    'binary': 'binary',
}
RESAMPLE_ALGS = {
    'continuous': 'bilinear',
    'nominal': 'nearest',
    'binary': 'nearest',
}


def plot_raster_list(tif_list, datatype_list, transform_list=None):
    raster_info = pygeoprocessing.get_raster_info(tif_list[0])
    bbox = raster_info['bounding_box']
    xy_ratio = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
    n_plots = len(tif_list)
    if xy_ratio <= 1:
        n_cols = 3
    if xy_ratio > 1:
        n_cols = 2
    if xy_ratio > 2:
        n_cols = 1
    n_rows = int(math.ceil(n_plots / n_cols))

    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(12, n_rows*4))

    # if colormap_list is None:
    #     colormap_list = ['viridis'] * n_plots
    if transform_list is None:
        transform_list = ['linear'] * n_plots
    for ax, tif, dtype, transform in zip(
            axes.flatten(), tif_list, datatype_list, transform_list):
        cmap = COLORMAPS[dtype]
        arr, resampled = read_masked_array(tif, RESAMPLE_ALGS[dtype])
        mappable = ax.imshow(arr, cmap=cmap, norm=transform)
        ax.set(title=f"{os.path.basename(tif)}{'*' if resampled else ''}")
        # ax.set_axis_off()
        fig.colorbar(mappable, ax=ax)
    [ax.set_axis_off() for ax in axes.flatten()]
    return fig


# TODO: this will probably end up in the geometamaker API
def geometamaker_load(filepath):
    with open(filepath, 'r') as file:
        yaml_string = file.read()
        yaml_dict = yaml.safe_load(yaml_string)
        if not yaml_dict or ('metadata_version' not in yaml_dict
                             and 'geometamaker_version' not in yaml_dict):
            message = (f'{filepath} exists but is not compatible with '
                       f'geometamaker.')
            raise ValueError(message)

    return geometamaker.geometamaker.RESOURCE_MODELS[yaml_dict['type']](**yaml_dict)


STATS_LIST = ['STATISTICS_VALID_PERCENT', 'STATISTICS_MINIMUM', 'STATISTICS_MAXIMUM', 'STATISTICS_MEAN']


def raster_workspace_summary(workspace):
    raster_summary = {}
    for path, dirs, files in os.walk(workspace):
        for file in files:
            if file.endswith('.yml'):
                filepath = os.path.join(path, file)
                try:
                    resource = geometamaker_load(filepath)
                except Exception as err:
                    print(filepath)
                    raise err
                if isinstance(resource, geometamaker.models.RasterResource):
                    name = os.path.basename(resource.path)
                    band = resource.get_band_description(1)
                    raster_summary[name] = {
                        k: v for k, v in band.gdal_metadata.items()
                        if k in STATS_LIST}
                    raster_summary[name]['units'] = band.units
    return pandas.DataFrame(raster_summary).T


def raster_inputs_summary(args_dict):
    raster_summary = {}
    for k, v in args_dict.items():
        if isinstance(v, str) and os.path.isfile(v):
            resource = geometamaker.describe(v, compute_stats=True)
            if isinstance(resource, geometamaker.models.RasterResource):
                name = os.path.basename(resource.path)
                band = resource.get_band_description(1)
                raster_summary[name] = {
                    k: v for k, v in band.gdal_metadata.items()
                    if k in STATS_LIST}
                raster_summary[name]['units'] = band.units
    return pandas.DataFrame(raster_summary).T


def table_description_to_md(filepath):
    resource = geometamaker.describe(filepath)
    fields = resource._get_fields()
    md_list = []
    for field in fields:
        if field.description:
            md_list.append(
                f"""
                **{field.name}** (units: {field.units})
                {field.description}
                """)
    return mo.md(''.join(md_list))
