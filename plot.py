#!/usr/bin/env python3
import json
import pathlib
from typing import Union

import fire
import matplotlib.pyplot as plt
import more_itertools
import pandas as pd
import seaborn as sns


def _rows(data):
    offset = {
        "2021": 18961,
        "2022": 19326,
        "2023": 19691,
    }[data["event"]]
    for member, member_data in data["members"].items():
        for day, day_data in member_data["completion_day_level"].items():
            day = int(day)
            for part, part_data in day_data.items():
                part = int(part)
                yield {
                    "member": int(member),
                    "day": day,
                    "part": part,
                    "ts": part_data["get_star_ts"] - 86400 * (day + offset) - 5 * 3600,
                    "stars": member_data["stars"],
                }


# How hard was the problem?
# Proxy: For each problem, how long did it take to solve the problem for members who compete on time
def _plot_difficulty(ax, df):
    member_stats = df.groupby("member")[["ts", "stars"]].max()
    active_members = frozenset(
        member_stats[
            (member_stats["ts"] < 86400)
            & (member_stats["stars"] == member_stats["stars"].max())
        ].index.values
    )
    df = df[df["member"].isin(active_members)]

    sns.boxplot(
        data=df,
        x="day",
        y="difficulty (hours)",
        hue="part",
        showfliers=False,
        palette=sns.color_palette("pastel"),
        ax=ax,
    )
    sns.stripplot(
        data=df,
        x="day",
        y="difficulty (hours)",
        hue="part",
        dodge=True,
        size=5,
        jitter=0.35,
        palette=sns.color_palette("deep"),
        ax=ax,
    )
    # Legend is more confusing than helpful and fixing is a pain
    ax.get_legend().remove()


# How many people lose interest?
# Proxy: For each problem, how many members completed the problem
# TODO: Consider changing definition of interest to also include members who completed a later problem
def _plot_engagement(ax, df):
    df["engagement (submissions)"] = 1
    df["active engagement (submissions)"] = df["ts"] < 86400
    df = (
        df.groupby(["day", "part"])[
            ["engagement (submissions)", "active engagement (submissions)"]
        ]
        .sum()
        .rename(columns={"member": "engagement (submissions)"})
        .reset_index()
    )
    sns.barplot(
        data=df,
        x="day",
        y="engagement (submissions)",
        hue="part",
        dodge=True,
        palette=sns.color_palette("deep"),
        ax=ax,
    )
    # Note that this number does not match the number of submissions for the
    # difficulty graph since here the days are independent
    x = sns.barplot(
        data=df,
        x="day",
        y="active engagement (submissions)",
        hue="part",
        dodge=True,
        palette=sns.color_palette("pastel"),
        ax=ax,
    )
    ax.set_ylabel("[active] engagement (submissions)")
    # Legend is more confusing than helpful and fixing is a pain
    ax.get_legend().remove()


def main(*paths: Union[None, str, pathlib.Path]):
    """Plot difficulty and engagement for private leaderboard

    :param paths: Location of json dumps from leaderboard api.
    """
    _, axs = plt.subplots(len(paths), 2, sharex=True, sharey="col")
    if len(paths) == 1:
        axs = [axs]

    for i, path in enumerate(paths):
        path = pathlib.Path(path)

        df = pd.DataFrame(_rows(json.loads(path.read_text())))
        df["difficulty (hours)"] = df["ts"] / 3600

        _plot_difficulty(axs[i][0], df)
        _plot_engagement(axs[i][1], df)
    plt.show()


if __name__ == "__main__":
    fire.Fire(main)
