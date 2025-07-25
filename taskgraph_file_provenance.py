import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium", app_title="Taskgraph File Graph")


@app.cell
def _():
    """Explore taskgaph database to understand file provenance.

    This notebook depends on experimental changes to the taskgraph db.
    Those changes are at https://github.com/davemfish/taskgraph/tree/exp/file-provenance
    """
    return


@app.cell
def _():
    import collections
    import json
    import os
    import sqlite3

    import geometamaker
    import pandas
    import marimo as mo
    import utils
    return collections, geometamaker, json, mo, os, pandas, sqlite3


@app.cell
def _(collections, os):
    def get_filepaths_from_args(args, file_set=None):
        if file_set is None:
            file_set = set()
        if isinstance(args, str):
            if os.path.exists(args):
                file_set.add(args)
            return file_set
        elif isinstance(args, collections.abc.Sequence):
            for arg in args:
                get_filepaths_from_args(arg, file_set)
        elif isinstance(args, collections.abc.Mapping):
            for k, v in args.items():
                get_filepaths_from_args(v, file_set)
        return file_set
    return (get_filepaths_from_args,)


@app.cell
def _(collections, geometamaker, os, pandas):
    STATS_LIST = ['STATISTICS_VALID_PERCENT', 'STATISTICS_MINIMUM', 'STATISTICS_MAXIMUM', 'STATISTICS_MEAN']
    def file_summary(file_list):
        summary = collections.defaultdict(dict)
        for filepath in file_list:
            resource = geometamaker.describe(filepath, compute_stats=True)
            name = os.path.basename(resource.path)
            if isinstance(resource, geometamaker.models.RasterResource):
                band = resource.get_band_description(1)
                summary[name] = {
                    k: v for k, v in band.gdal_metadata.items()
                    if k in STATS_LIST}
                summary[name]['units'] = band.units
            summary[name]['projection'] = resource.spatial.crs
            summary[name]['bounding_box'] = str(resource.spatial.bounding_box)
        
        return pandas.DataFrame(summary).T

    return (file_summary,)


app._unparsable_cell(
    r"""
    workspace = 'C:/Users/dmf/projects/invest/runs/sdr/sample-tg/'
    db_path = os.path.join(workspace, 'taskgraph_cache/taskgraph_data.db'
    """,
    name="_"
)


@app.cell
def _(db_path, pandas, sqlite3, workspace):
    con = sqlite3.connect(db_path)
    df = pandas.read_sql_query("SELECT * from target_files", con)
    df.filepath = df.filepath.apply(lambda x: x.replace(workspace.lower(), ''))
    con.close()
    return (df,)


@app.cell
def _(df, mo):
    table = mo.ui.table(df, pagination=False)
    table
    return (table,)


@app.cell
def _(file_summary, get_filepaths_from_args, json, mo, os, table, workspace):
    def tabulate(row):
        if row.filepath.any():
            selected_file = row.filepath.iloc[0]
            args_list = json.loads(row.args_list.iloc[0])
            kwargs_dict = json.loads(row.kwargs_dict.iloc[0])
            mo.output.replace(mo.md(
                f"""
                **{selected_file}**  
                Created by: {row.function_name.iloc[0]}
                """  
            ))
            args_files = get_filepaths_from_args(args_list)
            kwargs_files = get_filepaths_from_args(kwargs_dict)
            _table = mo.ui.table(
                file_summary([os.path.join(workspace, selected_file)] + list(args_files | kwargs_files)),
                pagination=False)
            mo.output.append(_table)

    tabulate(table.value)
    return


if __name__ == "__main__":
    app.run()
