from glob import glob
import pandas as pd
import warnings



def fetch_metadata_tables(metadata_path="valtiopaivat-persons/data"):
    """
    return a list of metadata tables.

    Args

        metadata_path (str): place to look for metadata tables

    returns

        list of pd.DataFrame objects
    """
    tables = []
    csv_files = glob(f"{metadata_path}/*.csv")
    for csv in csv_files:
        tables.append(pd.read_csv(csv))
    return tables


def join_metadata_tables(tables, key="swerik_person_id"):
    """
    Join metadata tables on a key. Return all possible combinations of data on the matching key.

    Args

        tables (list): list of pd dataFrame objects
        key (str): common column to merge on

    returns

        pandas df
    """
    assert len(tables) > 0
    if not isinstance(tables, list):
        raise TypeError("Expected a list")
    try:
        assert all(isinstance(_,pd.DataFrame) for _ in tables)
    except Exceptoin as e:
        print("expected a pandas dataframe", e)

    if len(tables) == 1:
        warnings.warn("I can't merge a table with itself. You get back what you put in.")
        return tables[0]
    else:
        inner_df = pd.merge(tables[0], tables[1], how='inner', on=key)
        outer_df = pd.merge(tables[0], tables[1], how='outer', on=key)
        if len(tables) > 2:
            for table in tables[2:]:
                inner_df = pd.merge(inner_df, table, how='inner', on=key)
                outer_df = pd.merge(outer_df, table, how='outer', on=key)
        return pd.concat([inner_df, outer_df]).drop_duplicates()


def fetch_metadata(metadata_path="valtiopaivat-persons/data"):
    """
    Get all metadata tables at metadata path and merge them to one df
    """
    return join_metadata_tables(fetch_metadata_tables(metadata_path=metadata_path)).sort_values(by=["swerik_person_id"])
