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
    import matplotlib.pyplot as plt
    return geopandas, mo, os, plt


@app.cell
def _():
    workspace = 'C:/Users/dmf/projects/forum/sdr/sample_3_16_0'
    watershed_results_vector = 'watershed_results_sdr_gura.shp'
    return watershed_results_vector, workspace


@app.cell
def _(geopandas, os, watershed_results_vector, workspace):
    ws_vector = geopandas.read_file(os.path.join(workspace, watershed_results_vector))
    return (ws_vector,)


@app.cell
def _(mo, ws_vector):
    mo.ui.table(ws_vector.drop(columns=['geometry']))
    return


@app.cell
def _(plt, ws_vector):
    fields = ["usle_tot", "sed_export", "sed_dep", "avoid_exp", "avoid_eros"]
    fig, [[ax1, ax2, ax3], [ax4, ax5, ax6]] = plt.subplots(2, 3, figsize=(15, 4))
    for ax, field in zip([ax1, ax2, ax3, ax4, ax5], fields):
        ws_vector.plot(ax=ax, column=field, cmap="Greens", edgecolor='lightgray')
        ax.set(title=f"{field}")
        ax.set_axis_off()
    ws_vector.plot(ax=ax6, facecolor="none", edgecolor='lightgray')
    ws_vector.apply(lambda x: ax6.annotate(text=x['ws_id'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1);
    ax6.set_axis_off()
    fig
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
