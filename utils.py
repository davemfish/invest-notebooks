import math
import os

import geometamaker
import numpy
import pygeoprocessing
import matplotlib.pyplot as plt
import marimo as mo
import yaml


def read_masked_array(filepath):
    nodata = pygeoprocessing.get_raster_info(filepath)['nodata']
    array = pygeoprocessing.raster_to_numpy_array(filepath)
    masked_array = numpy.where(array == nodata, numpy.nan, array)
    return masked_array


def plot_raster_list(tif_list, colormap='viridis'):
    n_plots = len(tif_list)
    n_cols = n_plots
    n_rows = 1
    if n_plots > 4:
        n_cols = 4
        n_rows = int(math.ceil(n_plots / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*3, n_rows*3))
    for ax, tif in zip(axes.flatten(), tif_list):
        arr = read_masked_array(tif)
        ax.imshow(arr, cmap=colormap)
        ax.set(title=f"{os.path.basename(tif)}")
        ax.set_axis_off()
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
