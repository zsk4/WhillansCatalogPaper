import marimo

__generated_with = "0.9.14"
app = marimo.App()


@app.cell
def __():
    import os
    import pandas as pd
    import src.Catalog.Catalog as Catalog

    year = 2010
    st = 0
    ed = -1
    catalog = []
    for _event in os.listdir(f"{year}_{year}events_2stas"):
        catalog.append(
            pd.read_csv(f"{year}_{year}events_2stas/{_event}", sep="\t", index_col=0)
        )
    return Catalog, catalog, ed, os, pd, st, year


@app.cell
def __(Catalog, catalog, ed, st):
    print(len(catalog))
    for _event in catalog[st:ed]:
        Catalog.plot_event(_event)
    return


if __name__ == "__main__":
    app.run()
