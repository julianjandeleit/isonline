# %%
import numpy as np
import pandas as pd
from datetime import datetime
import altair as alt
import colorcet as cc
from toolz import pipe

# %% read data

incidences = pd.read_csv("demodata", sep=" ", header=0)
incidences
incidences = incidences.drop(columns=incidences.columns[2:])
incidences
incidences = incidences.rename(columns=dict(
    zip(incidences.columns, ["date", "time"])))
incidences


incidences["date"] = incidences["date"].apply(
    lambda x: datetime.strptime(x, "%Y-%m-%d"))

# replace time with hour
incidences["hour"] = incidences["time"].apply(lambda x:
                                              datetime.strptime(
                                                  x, "%H:%M:%S").hour
                                              )
incidences


#incidences = incidences.drop(columns=["time"]); incidences

# %% group by date
hour_counts = incidences.groupby(["date"], as_index=True)[
    "hour"].value_counts()
hour_counts

incidences = incidences.set_index(["date", "hour"])
incidences["count"] = hour_counts

incidences = incidences.reset_index()
incidences

# %% build plot

#  select data relevant for plot
min_date = min(incidences.date)
max_date = max(incidences.date)

prange = pipe(
    pd.period_range(min_date, max_date).to_timestamp(),
    lambda x: pd.DataFrame(x),
    #    lambda x: x.assign(hour=pd.NaT,count=pd.NaT),
    lambda x: x.rename(columns={0: "date"}),
    lambda x: x.set_index("date")
)
prange

dhc = incidences[["date", "hour", "count"]]
dhc = dhc.set_index("date")
dhc = prange.join(dhc)
dhc = dhc.fillna(0)
dhc

hrange = pipe(
    list(range(24)),
    lambda x: pd.DataFrame(x),
    lambda x: x.rename(columns={0: "hour"}),
    lambda x: x.set_index("hour")
)

dhc = hrange.join(dhc.reset_index().set_index("hour")).reset_index()

dhc["count"] = dhc["count"].fillna(0.0)
dhc["date"] = dhc["date"].fillna(min_date)
dhc = dhc.drop(dhc[dhc["count"] == 0.0].index)

# %%
# altair visualization

chart = alt.Chart(dhc).mark_rect().encode(
    alt.X('monthdate(date):N', title="Date"),
    alt.Y('hour:N', title="Hour of Day"),
    alt.Color('count:O', legend=alt.Legend(
        title="Failure Count", description="measured every 5 minutes"))
).properties(
    title={
        "text": 'Failure Incidences 2022',
        "subtitle": 'Measured every 5 Minutes'}
).interactive()

chart.save("fig.html")
# %%
