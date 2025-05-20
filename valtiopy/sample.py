import hashlib
import numpy as np
import os
import pandas as pd




def goldstandard(df, n=3, by=["year", "estate"], seed=None, scope="dir", sampled_format="pdf"):
    """
    Draw a goldstandard sample of N documents per stratum

    Args

        - df (pandas DataFrame): DF from which to draw a sample. It should have a column `path` and a column for each of the strata
        - n (int): number of items to draw
        - by (list): list of strata to stratify with
        - seed (str): a random state
        - scope (str): "dir" or "file". If path is a `dir`, this will sample from all files in the directory. if scope is `file` this will sample the paths in the path column
        - sampled_format (str): this function uses the alto xml files to draw a sample (easier to store all locally), but often we want PDF files. If this option is set to "pdf" the path will be corrected in the resulting sample to the PDF

    Return

        - list
    """

    #for stratum in strata:
    #    print(stratum)
    #    df_stratum = df[df[by] == stratum]
       #data.append(df_strata.sample(n, random_state=random_state))
        #return pd.concat(data).reset_index(drop=True)

    def _sample_dir(x, sample_, n, random_state=None):
        files_ = []
        x = list(x["path"])
        for _ in x:
            files_.extend([f"{_}/{file_}" for file_ in os.listdir(_)])
        s = pd.Series(files_).sample(n=n, random_state=random_state).to_list()
        sample_.extend(s)
        return sample_

    if seed is not None:
        seed = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % (2**32)
    if scope == 'file':
        sample_ = df.groupby(by, group_keys=False).apply(lambda x: x.sample(n, random_state=seed), include_groups=False)
        sample_ = list(sample_["path"])
    elif scope == 'dir':
        sampled_ = []
        sample_ = df.groupby(by, group_keys=False).apply(lambda x: _sample_dir(x, sampled_, n, random_state=seed), include_groups=False)
        sample_=sampled_

    if sampled_format == "pdf":
        sample_ = [_.replace("-alto", "-pdf").replace(".xml", ".pdf") for _ in sample_]
    return sample_



if __name__ == '__main__':
    rows1 = [
        ["file1", "1992", "a"],
        ["file2", "1992", "b"],
        ["file3", "1992", "c"],
        ["file4", "1993", "a"],
        ["file11", "1993", "b"],
        ["file5", "1994", "a"],
        ["file12", "1994", "b"],
        ["file6", "1995", "a"],
        ["file7", "1995", "b"],
        ["file8", "1995", "c"],
        ["file9", "1996", "b"],
        ["file13", "1996", "a"],
        ["file10", "1997", "c"],
        ["file14", "1997", "b"],
        ["file15", "1997", "a"],
        ["file11", "1992", "a"],
        ["file12", "1992", "b"],
        ["file113", "1992", "c"],
        ["file114", "1993", "a"],
        ["file1111", "1993", "b"],
        ["file115", "1994", "a"],
        ["file112", "1994", "b"],
        ["file16", "1995", "a"],
        ["file17", "1995", "b"],
        ["file18", "1995", "c"],
        ["file19", "1996", "b"],
        ["file1113", "1996", "a"],
        ["file111110", "1997", "c"],
        ["file111114", "1997", "b"],
        ["file151111", "1997", "a"],
        ["file17", "1992", "a"],
        ["file27", "1992", "b"],
        ["file37", "1992", "c"],
        ["file47", "1993", "a"],
        ["file171", "1993", "b"],
        ["file57", "1994", "a"],
        ["file127", "1994", "b"],
        ["file67", "1995", "a"],
        ["file77", "1995", "b"],
        ["file87", "1995", "c"],
        ["file97", "1996", "b"],
        ["file173", "1996", "a"],
        ["file107", "1997", "c"],
        ["file147", "1997", "b"],
        ["file157", "1997", "a"],
    ]

    rows2 = [
        ['valtiopaivat-records-alto/data/1882/ptk_1882_talonpojat_I', '1882', 'talonpojat'],
        ['valtiopaivat-records-alto/data/1882/ptk_1882_talonpojat_II', '1882', 'talonpojat'],
        ['valtiopaivat-records-alto/data/1900/prot_1900_adeln_lll', "1900", "adeln"],
        ['valtiopaivat-records-alto/data/1900/prot_1900_adeln_II', "1900", "adeln"],
        ['valtiopaivat-records-alto/data/1900/prot_1900_adeln_I', "1900", "adeln"],
        ['valtiopaivat-records-alto/data/1877-1878/prot_1877-1878_borgare_IV', '1877-1878', 'borgare'],
        ['valtiopaivat-records-alto/data/1877-1878/prot_1877-1878_borgare_III', '1877-1878', 'borgare'],
        ['valtiopaivat-records-alto/data/1877-1878/prot_1877-1878_borgare_II', '1877-1878', 'borgare'],
        ['valtiopaivat-records-alto/data/1877-1878/prot_1877-1878_borgare_I', '1877-1878', 'borgare'],
        ['valtiopaivat-records-alto/data/1877/prot_1877_adeln_II', "1877", "adeln"],
        ['valtiopaivat-records-alto/data/1885/prot_1885_borgare_I', "1885", "borgare"],
    ]
    cols = ["path", "year", "estate"]
    df1 = pd.DataFrame(rows1, columns=cols)
    df2 = pd.DataFrame(rows2, columns=cols)

    print("Running goldstandard test 1: sample files")

    [print(_) for _ in goldstandard(df1, n=1, scope="file")]

    print("Running goldstandard test 2: sample files from dir")

    [print(_) for _ in goldstandard(df2, n=3, scope="dir")]
