import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium", app_title="Pollination explore")


@app.cell
def _():
    import glob
    import os

    import marimo as mo
    import geopandas
    import geometamaker
    import matplotlib.pyplot as plt
    from natcap.invest import datastack
    import pandas
    return datastack, geopandas, glob, mo, os, pandas


@app.cell
def _():
    workspace = 'C:/Users/dmf/projects/forum/pollination/sample'
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
def _(biophys_table, mo):
    mo.ui.table(biophys_table)
    return


@app.cell
def _(farm_vector_path, geopandas, os, workspace):
    vector = geopandas.read_file(os.path.join(workspace, farm_vector_path))
    return (vector,)


@app.cell
def _(mo, vector):
    mo.ui.table(vector.drop(columns=['geometry']))
    return


@app.cell
def _():
    # fields = ["usle_tot", "sed_export", "sed_dep", "avoid_exp", "avoid_eros"]
    # fig, [[ax1, ax2, ax3], [ax4, ax5, ax6]] = plt.subplots(2, 3, figsize=(15, 4))
    # for ax, field in zip([ax1, ax2, ax3, ax4, ax5], fields):
    #     ws_vector.plot(ax=ax, column=field, cmap="Greens", edgecolor='lightgray')
    #     ax.set(title=f"{field}")
    #     ax.set_axis_off()
    # ws_vector.plot(ax=ax6, facecolor="none", edgecolor='lightgray')
    # ws_vector.apply(lambda x: ax6.annotate(text=x['ws_id'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1);
    # ax6.set_axis_off()
    # fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### NoData Summary""")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
