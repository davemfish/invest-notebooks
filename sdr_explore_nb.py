# /// script
# dependencies = [
#   geopandas,
#   matplotlib
# ]
# ///

import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium", app_title="SDR explore")


@app.cell
def _():
    import os

    import marimo as mo
    import geopandas
    import geometamaker
    from natcap.invest.sdr import sdr
    from natcap.invest import datastack
    import natcap.invest.utils
    import matplotlib.pyplot as plt
    import pygeoprocessing
    import yaml

    import utils
    return (
        datastack,
        geometamaker,
        geopandas,
        mo,
        natcap,
        os,
        plt,
        pygeoprocessing,
        utils,
        yaml,
    )


@app.cell
def _(datastack, mo):
    logfile_path = mo.cli_args().get('logfile')
    _, ds_info = datastack.get_datastack_info(logfile_path)
    args_dict = ds_info.args
    return (args_dict,)


@app.cell
def _(args_dict, natcap):
    # workspace = 'C:/Users/dmf/projects/forum/sdr/sample_3_16_0'
    # watershed_results_vector = 'watershed_results_sdr_gura.shp'
    workspace = args_dict['workspace_dir']
    suffix_str = natcap.invest.utils.make_suffix_string(args_dict, 'results_suffix')
    watershed_results_vector = f'watershed_results_sdr{suffix_str}.shp'
    return suffix_str, watershed_results_vector, workspace


@app.cell
def _(geopandas, os, watershed_results_vector, workspace):
    ws_vector = geopandas.read_file(os.path.join(workspace, watershed_results_vector))
    return (ws_vector,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Results by Watershed""")
    return


@app.cell
def _(mo, ws_vector):
    mo.ui.table(ws_vector.drop(columns=['geometry']))
    return


@app.cell
def _(plt, ws_vector):
    def _plot():
        fields = ["usle_tot", "sed_export", "sed_dep", "avoid_exp", "avoid_eros"]
        fig, [[ax1, ax2, ax3], [ax4, ax5, ax6]] = plt.subplots(2, 3, figsize=(15, 4))
        for ax, field in zip([ax1, ax2, ax3, ax4, ax5], fields):
            ws_vector.plot(ax=ax, column=field, cmap="Greens", edgecolor='lightgray')
            ax.set(title=f"{field}")
            ax.set_axis_off()
        ws_vector.plot(ax=ax6, facecolor="none", edgecolor='lightgray')
        ws_vector.apply(lambda x: ax6.annotate(text=x['ws_id'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1);
        ax6.set_axis_off()
        return fig
    _plot()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Stream Network""")
    return


@app.cell
def _(math, os, plt, pygeoprocessing, suffix_str, utils, workspace):
    streams_raster_path = os.path.join(workspace, f'stream{suffix_str}.tif')
    dem_raster_path = os.path.join(workspace, 'intermediate_outputs', f'pit_filled_dem{suffix_str}.tif')
    drains_to_stream_path = os.path.join(workspace, 'intermediate_outputs', f'what_drains_to_stream{suffix_str}.tif')

    raster_info = pygeoprocessing.get_raster_info(dem_raster_path)
    bbox = raster_info['bounding_box']
    xy_ratio = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
    print(xy_ratio)

    def plot_raster_list(tif_list, colormap='viridis', row_major=True):
        n_plots = len(tif_list)
        n_cols = n_plots
        n_rows = 1
        if n_plots > 4:
            n_cols = 4
            n_rows = int(math.ceil(n_plots / n_cols))
        if not row_major:
            nc = n_cols
            n_cols = n_rows
            n_rows = nc
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*xy_ratio*2, n_rows*2))
        for ax, tif in zip(axes.flatten(), tif_list):
            arr = utils.read_masked_array(tif)
            ax.imshow(arr, cmap=colormap)
            ax.set(title=f"{os.path.basename(tif)}")
            ax.set_axis_off()
        return fig

    fig = plot_raster_list([streams_raster_path, dem_raster_path, drains_to_stream_path], row_major=False)
    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### NoData Summary""")
    return


@app.cell
def _(geometamaker, yaml):
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
    return (geometamaker_load,)


@app.cell
def _(geometamaker, geometamaker_load, os, pandas, workspace):
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
                    band = resource.get_band_description(1)
                    raster_summary[os.path.basename(resource.path)] = band.gdal_metadata
    pandas.DataFrame(raster_summary)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
