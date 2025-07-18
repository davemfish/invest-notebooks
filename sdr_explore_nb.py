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
    import math
    import os

    import geopandas
    import geometamaker
    import marimo as mo
    import matplotlib.pyplot as plt
    from natcap.invest.sdr import sdr
    from natcap.invest import datastack
    from natcap.invest import spec
    import natcap.invest.utils

    import pandas
    import pygeoprocessing
    import yaml

    import utils
    return (
        datastack,
        geopandas,
        math,
        mo,
        natcap,
        os,
        plt,
        pygeoprocessing,
        utils,
    )


@app.cell
def _(datastack, mo):
    logfile_path = mo.cli_args().get('logfile')
    _, ds_info = datastack.get_datastack_info(logfile_path)
    args_dict = ds_info.args
    mo.accordion({'SDR model arguments': args_dict})
    return (args_dict,)


@app.cell
def _(args_dict, natcap):
    # workspace = 'C:/Users/dmf/projects/forum/sdr/sample_3_16_0'
    # watershed_results_vector = 'watershed_results_sdr_gura.shp'
    workspace = args_dict['workspace_dir']
    suffix_str = natcap.invest.utils.make_suffix_string(args_dict, 'results_suffix')
    return suffix_str, workspace


@app.cell
def _(geopandas, os, suffix_str, workspace):
    watershed_results_vector_path = os.path.join(workspace, f'watershed_results_sdr{suffix_str}.shp')
    ws_vector = geopandas.read_file(watershed_results_vector_path)
    return watershed_results_vector_path, ws_vector


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Results by Watershed""")
    return


@app.cell
def _(mo, ws_vector):
    mo.ui.table(ws_vector.drop(columns=['geometry']))
    return


@app.cell
def _(utils, watershed_results_vector_path):
    utils.table_description_to_md(watershed_results_vector_path)
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


@app.cell
def _(mo, os, plot_raster_list, suffix_str, workspace):
    _raster_cmap_list = (
        (os.path.join(workspace, f'avoided_erosion{suffix_str}.tif'), 'viridis', 'linear'),
        (os.path.join(workspace, f'avoided_export{suffix_str}.tif'), 'viridis', 'log'),
        (os.path.join(workspace, f'sed_deposition{suffix_str}.tif'), 'viridis', 'log'),
        (os.path.join(workspace, f'sed_export{suffix_str}.tif'), 'viridis', 'log'),
        (os.path.join(workspace, f'rkls{suffix_str}.tif'), 'viridis', 'linear'),
        (os.path.join(workspace, f'usle{suffix_str}.tif'), 'viridis', 'log')
    )

    _tif_list, _cmap_list, _transform_list = zip(*_raster_cmap_list)

    _figure = plot_raster_list(
        _tif_list,
        colormap_list=_cmap_list,
        transform_list=_transform_list,
        row_major=True)

    mo.accordion({'Raster Results': _figure})
    return


@app.cell
def _(math, mo, os, plt, pygeoprocessing, suffix_str, utils, workspace):
    streams_raster_path = os.path.join(workspace, f'stream{suffix_str}.tif')
    dem_raster_path = os.path.join(workspace, 'intermediate_outputs', f'pit_filled_dem{suffix_str}.tif')
    drains_to_stream_path = os.path.join(workspace, 'intermediate_outputs', f'what_drains_to_stream{suffix_str}.tif')

    def plot_raster_list(tif_list, colormap_list=None, transform_list=None, row_major=True):
        raster_info = pygeoprocessing.get_raster_info(tif_list[0])
        bbox = raster_info['bounding_box']
        xy_ratio = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
        n_plots = len(tif_list)
        n_cols = n_plots
        n_rows = 1
        if n_plots > 2:
            n_cols = 2
            n_rows = int(math.ceil(n_plots / n_cols))
        if not row_major:
            nc = n_cols
            n_cols = n_rows
            n_rows = nc
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*xy_ratio*2, n_rows*2))

        if colormap_list is None:
            colormap_list = ['viridis'] * n_plots
        if transform_list is None:
            transform_list = ['linear'] * n_plots
        for ax, tif, cmap, transform in zip(axes.flatten(), tif_list, colormap_list, transform_list):
            arr = utils.read_masked_array(tif)
            mappable = ax.imshow(arr, cmap=cmap, norm=transform)
            ax.set(title=f"{os.path.basename(tif)}")
            ax.set_axis_off()
            fig.colorbar(mappable, ax=ax)
        return fig

    _figure = plot_raster_list(
        [streams_raster_path, dem_raster_path, drains_to_stream_path],
        colormap_list=['binary', 'Greys', 'binary'],
        row_major=False)
    mo.accordion({'Stream Network Maps': _figure})
    return (plot_raster_list,)


@app.cell
def _(args_dict, mo, utils, workspace):
    _output_raster_stats = utils.raster_workspace_summary(workspace)
    _input_raster_stats = utils.raster_inputs_summary(args_dict)
    mo.accordion({
        'Output Raster Stats': _output_raster_stats,
        'Input Raster Stats': _input_raster_stats,
    }, multiple=True)
    return


@app.cell
def _(args_dict, mo, plot_raster_list):
    _raster_cmap_list = (
        (args_dict['dem_path'], 'Greys'),
        (args_dict['erodibility_path'], 'viridis'),
        (args_dict['erosivity_path'], 'viridis'),
        (args_dict['lulc_path'], 'Set3')
    )

    # This arg is optional and may not exist
    if args_dict['drainage_path']:
        _raster_cmap_list.append(args_dict['drainage_path'], 'binary')

    _tif_list, _cmap_list, = zip(*_raster_cmap_list)

    _figure = plot_raster_list(
        _tif_list,
        colormap_list=_cmap_list,
        row_major=False)

    mo.accordion({'Input Maps': _figure})
    return


if __name__ == "__main__":
    app.run()
