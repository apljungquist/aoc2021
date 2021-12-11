import json
import pathlib

import matplotlib.pyplot as plt
import more_itertools
import pandas as pd
import seaborn as sns


def _rows(data):
    offset = 18961
    for member, member_data in data["members"].items():
        for day, day_data in member_data["completion_day_level"].items():
            day = int(day)
            for part, part_data in day_data.items():
                part = int(part)
                yield {
                    "member": member,
                    "day": day,
                    "part": part,
                    "ts": part_data["get_star_ts"] - 86400 * (day + offset) - 5 * 3600,
                }


def main():
    path = more_itertools.one(pathlib.Path(__file__).with_suffix("").glob("*.json"))
    df = pd.DataFrame(_rows(json.loads(path.read_text())))
    df["dt"] = pd.to_datetime(df["ts"], unit="s")
    df["minutes"] = df["ts"] / 60
    df["hours"] = df["ts"] / 3600
    df["x"] = df["day"] + df["part"] / 4 - 0.5

    participants = (
        df.groupby(["day", "part"])
        .count()[["member"]]
        .rename(columns={"member": "total"})
    )
    participants["active"] = (
        df[df["ts"] < 86400].groupby(["day", "part"]).count()["member"]
    )
    print(participants.to_string())

    data = df[df["ts"] < 86400]
    sns.boxplot(
        data=data,
        x="day",
        y="hours",
        hue="part",
        showfliers=False,
        # saturation=0,
        palette=sns.color_palette("pastel"),
    )
    sns.stripplot(
        data=data,
        x="day",
        y="hours",
        hue="part",
        dodge=True,
        size=5,
        jitter=0.35,
        palette=sns.color_palette("deep")
        # color="0.25",
    )
    plt.show()


if __name__ == "__main__":
    main()
