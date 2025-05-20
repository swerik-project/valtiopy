"""
Plot stuff
"""
from cycler import cycler
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_speaker_mapping(df, out_path="test/result/speaker-mapping.png"):
    """
    Plot mapped vs unmapped speaker introductions

    Args

        d: dictionary prouced by test.known-speakers
        out_path: where the plot gets written

    Return

        nothing, but writes a plot
    """
    estates = df["estate"].unique()
    print(estates)
    colors = list('kkbbggrrcc')
    default_cycler = (cycler(color=colors) +
                      cycler(linestyle=(['-', '--']*5)) +
                      cycler(linewidth=([2, 1.25]*5))
                      )
    plt.rc('axes', prop_cycle=default_cycler)
    f, ax = plt.subplots(figsize=(16,7))
    legend_text = []
    ddf = df.groupby("year")[["total", "matched"]].sum().reset_index()
    x = ddf['year'].tolist()
    for count in ["total", "matched"]:
        legend_text.append(f"ALL:{count}")
        Y = ddf[count].tolist()
        X, Y = zip(*sorted(zip(x,Y),key=lambda x:x[0]))
        plt.plot(X,Y)
    for estate in estates:
        print(estate)
        dfv = df.loc[df["estate"] == estate]
        x = dfv['year'].tolist()
        for count in ["total", "matched"]:
            legend_text.append(f"{estate}:{count}")
            Y = dfv[count].tolist()
            X, Y = zip(*sorted(zip(x,Y),key=lambda x:x[0]))
            plt.plot(X,Y)
    plt.title('Coverage of matched speakers vs total speakers')
    plt.legend(legend_text, loc ="upper right")
    ax.set_xlabel('Year')
    ax.tick_params(axis='x', labelrotation=90)
    plt.savefig(out_path, dpi=300)



def plot_speaker_mapping_proportion(df, out_path="test/result/speaker-mapping-proportion.png"):
    """
    Plot mapped vs unmapped speaker introductions

    Args

        d: dictionary prouced by test.known-speakers
        out_path: where the plot gets written

    Return

        nothing, but writes a plot
    """
    estates = df["estate"].unique()
    print(estates)
    colors = list('kbgrc')
    default_cycler = (cycler(color=colors) +
                      cycler(linestyle=(['-', '--', '--', '--', '--'])) +
                      cycler(linewidth=([2, 1.25, 1.25, 1.25, 1.25]))
                      )
    plt.rc('axes', prop_cycle=default_cycler)
    f, ax = plt.subplots(figsize=(16,7))
    ddf = df.groupby("year")[["total", "matched"]].sum().reset_index()
    lab = ["total"]
    ddf["proportion"] = ddf.apply(lambda x: x["matched"]/x["total"], axis=1)
    x = ddf['year'].tolist()
    y = ddf['proportion'].tolist()
    X, Y = zip(*sorted(zip(x,y),key=lambda x:x[0]))
    plt.plot(X,Y)
    for estate in estates:
        lab.append(estate)
        dfv = df.loc[df["estate"] == estate]
        dfv["proportion"] = dfv.apply(lambda x: x["matched"]/x["total"], axis=1)
        x = dfv['year'].tolist()
        y = dfv['proportion'].tolist()
        X, Y = zip(*sorted(zip(x,y),key=lambda x:x[0]))
        plt.plot(X,Y)
    plt.title('Coverage of matched speakers vs total speakers')
    plt.legend(lab, loc ="upper right")
    ax.set_xlabel('Year')
    ax.tick_params(axis='x', labelrotation=90)
    plt.savefig(out_path, dpi=300)
