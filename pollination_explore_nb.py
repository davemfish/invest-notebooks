import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium", app_title="Pollination explore")


@app.cell
def _():
    import glob
    import math
    import os

    import marimo as mo
    import geopandas
    import geometamaker
    import matplotlib.pyplot as plt
    from natcap.invest import datastack
    import numpy
    import pandas
    import pygeoprocessing
    return (
        datastack,
        geopandas,
        glob,
        math,
        mo,
        numpy,
        os,
        pandas,
        plt,
        pygeoprocessing,
    )


@app.cell
def _():
    # workspace = 'C:/Users/dmf/projects/forum/pollination/sample'
    workspace = 'C:/Users/dmf/projects/forum/pollination/sample_no_summer_fix'
    farm_vector_path = 'farm_results.shp'
    return farm_vector_path, workspace


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Input Data""")
    return


@app.cell
def _(datastack, glob, os, workspace):
    logfile_path = glob.glob(os.path.join(workspace, '*.txt'))[0]
    _, datastack_info = datastack.get_datastack_info(logfile_path)
    args_dict = datastack_info.args
    args_dict
    # datastack_info.invest_version
    return (args_dict,)


@app.cell
def _(args_dict, pandas):
    guild_table = pandas.read_csv(args_dict['guild_table_path'])
    biophys_table = pandas.read_csv(args_dict['landcover_biophysical_table_path'])
    return biophys_table, guild_table


@app.cell
def _(guild_table, mo):
    mo.ui.table(guild_table)
    return


@app.cell
def _(args_dict, numpy, os, plt, pygeoprocessing, workspace):
    lulc_tif = os.path.join(workspace, args_dict['landcover_raster_path'])
    def plot_lulc(filepath):
        nodata = pygeoprocessing.get_raster_info(filepath)['nodata']
        array = pygeoprocessing.raster_to_numpy_array(filepath)
        masked_array = numpy.where(array == nodata, numpy.nan, array)
        return plt.imshow(masked_array, cmap='Dark2')
    plot_lulc(lulc_tif)
    return


@app.cell
def _(biophys_table, mo):
    mo.ui.table(biophys_table)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Farm Results""")
    return


@app.cell
def _(farm_vector_path, geopandas, mo, os, workspace):
    farm_vector = geopandas.read_file(os.path.join(workspace, farm_vector_path))
    mo.ui.table(farm_vector.drop(columns=['geometry']))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Pollinator Supply, based on 
    - available nesting sites in each cell,  
    - the floral resources (i.e., food) in surrounding cells. Floral resources in cells near nesting sites are given more weight than distant cells, according to the species’ average foraging range.  
    - and the relative abundance of that pollinator species.
    """
    )
    return


@app.cell
def _(glob, numpy, os, plt, pygeoprocessing, workspace):
    # Pollinator Supply
    supply_tifs = glob.glob(os.path.join(workspace, 'pollinator_supply*.tif'))

    def read_masked_array(filepath):
        nodata = pygeoprocessing.get_raster_info(filepath)['nodata']
        array = pygeoprocessing.raster_to_numpy_array(filepath)
        masked_array = numpy.where(array == nodata, numpy.nan, array)
        return masked_array

    n_plots = len(supply_tifs)
    fig, axes = plt.subplots(1, n_plots, figsize=(12, 4))
    for ax, tif in zip(axes, supply_tifs):
        arr = read_masked_array(tif)
        ax.imshow(arr, cmap='viridis')
        ax.set(title=f"{os.path.basename(tif).replace('pollinator_supply_', '')}")
        ax.set_axis_off()
    fig.suptitle('Pollinator Supply')
    return (read_masked_array,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Pollinator Abundance
    Pollinator supply is an indicator of where pollinators originate from on the landscape. Pollinator abundance indicates where pollinators are active on the landscape. Pollinator abundance depends on,  

    - the floral resources that attract pollinators to a cell  
    - the supply of pollinators that can access that cell.
    """
    )
    return


@app.cell
def _(math, os, plt, read_masked_array):
    def plot_abundance(tif_list):
        n_plots = len(tif_list)
        n_cols = n_plots
        n_rows = 1
        if n_plots > 4:
            n_cols = 4
            n_rows = int(math.ceil(n_plots / n_cols))
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*3, n_rows*3))
        for ax, tif in zip(axes.flatten(), tif_list):
            arr = read_masked_array(tif)
            ax.imshow(arr, cmap='viridis')
            ax.set(title=f"{os.path.basename(tif).replace('pollinator_abundance_', '')}")
            ax.set_axis_off()
        return fig
    return (plot_abundance,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Species Abundance""")
    return


@app.cell
def _(glob, os, plot_abundance, workspace):
    # Pollinator Abundance (species)
    abundance_tifs = glob.glob(os.path.join(workspace, 'pollinator_abundance*.tif'))
    plot_abundance(abundance_tifs)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Total Abundance""")
    return


@app.cell
def _():
    return


@app.cell
def _(glob, os, plot_abundance, workspace):
    total_abundance_tifs = glob.glob(os.path.join(workspace, 'total_pollinator_abundance*.tif'))
    plot_abundance(total_abundance_tifs)
    return


@app.cell
def _(
    farm_vector_path,
    glob,
    os,
    plot_abundance,
    pprint,
    pygeoprocessing,
    workspace,
):
    ## Farm Pollinator Abundance
    farm_abundance_tifs = glob.glob(os.path.join(workspace, 'intermediate_outputs', 'farm_pollinator*.tif'))
    farm_abundance_tifs.extend(glob.glob(os.path.join(workspace, 'farm_pollinator*.tif')))
    plot_abundance(farm_abundance_tifs)
    for fa_tif in farm_abundance_tifs:
        print(f'{os.path.basename(fa_tif)}')
        fa_stats = pygeoprocessing.zonal_statistics((fa_tif, 1), os.path.join(workspace, farm_vector_path))
        pprint.pprint(fa_stats)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Yields""")
    return


@app.cell
def _(farm_vector_path, glob, os, pygeoprocessing, workspace):
    ## Yields
    import pprint
    yield_tifs = glob.glob(os.path.join(workspace, '*_pollinator_yield*.tif'))
    # plot_abundance(yield_tifs)
    for yield_tif in yield_tifs:
        print(f'{os.path.basename(yield_tif)}')
        stats = pygeoprocessing.zonal_statistics((yield_tif, 1), os.path.join(workspace, farm_vector_path))
        pprint.pprint(stats)
        # yield_array = read_masked_array(yield_tif)
        # print(f'{os.path.basename(yield_tif)}: {numpy.nansum(yield_array)}')
    return (pprint,)


@app.cell
def _(farm_vector_path, glob, os, pprint, pygeoprocessing, workspace):
    # Managed Pollinator
    managed_pollinator_tif = glob.glob(os.path.join(workspace, 'intermediate_outputs', 'managed_pollinators*.tif'))[0]
    managed_stats = pygeoprocessing.zonal_statistics((managed_pollinator_tif, 1), os.path.join(workspace, farm_vector_path))
    pprint.pprint(managed_stats)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    Wild pollinator yield on a farm = total pollinator yield - managed pollinator yield  
    0 = 0.9 - 0.9  
    Total pollinator yield = managed + farm abundance  
    0.9 = 0.9 + 0

    Why is farm abundance 0 on the first farm?

    Farm abundance (spring) is a product of half_sat (spring) and total pollinator abundance
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r""" """)
    return


if __name__ == "__main__":
    app.run()
