#%%
import numpy as np
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import colorcet as cc
from toolz import pipe

#%% read data

incidences = pd.read_csv("demodata",sep=" ",header=0); incidences
incidences = incidences.drop(columns=incidences.columns[2:]); incidences
incidences = incidences.rename(columns=dict(zip(incidences.columns,["date", "time"]))); incidences


incidences["date"] = incidences["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))

# replace time with hour
incidences["hour"] = incidences["time"].apply(lambda x: 
    datetime.strptime(x,"%H:%M:%S").hour
    ); incidences


#incidences = incidences.drop(columns=["time"]); incidences

#%% group by date
hour_counts = incidences.groupby(["date"],as_index=True)["hour"].value_counts(); hour_counts

incidences = incidences.set_index(["date","hour"])
incidences["count"] = hour_counts

incidences = incidences.reset_index(); incidences

#%% build plot

#  select data relevant for plot
min_date = min(incidences.date)
max_date = max(incidences.date)

prange = pipe(
    pd.period_range(min_date,max_date).to_timestamp(),
    lambda x: pd.DataFrame(x),
#    lambda x: x.assign(hour=pd.NaT,count=pd.NaT),
    lambda x: x.rename(columns={0:"date"}),
    lambda x: x.set_index("date")
    )
prange

dhc = incidences[["date","hour","count"]]
dhc = dhc.set_index("date")
dhc = prange.join(dhc)
dhc = dhc.fillna(0)
dhc

hrange = pipe(
    list(range(24)),
    lambda x: pd.DataFrame(x),
    lambda x: x.rename(columns={0:"hour"}),
    lambda x: x.set_index("hour")
)

dhc = hrange.join(dhc.reset_index().set_index("hour")).reset_index()
dhc["count"] = dhc["count"].fillna(0.0)
dhc["date"] = dhc["date"].fillna(min_date)
dhc

#%%
table = dhc.pivot_table(index="hour",columns="date",values="count",fill_value=0)
table[table == 0.0] = np.nan

plt.figure(figsize=(40,5))
g = sns.heatmap(table,cbar_kws={'label': 'incidence frequency'},cmap=cc.cm.kr,square=True)

unique_months = pd.DataFrame(list(dhc.reset_index().date.apply(lambda x: (x.year,x.month,x.day)).unique()))
unique_months = unique_months.groupby([0,1]).min().reset_index()
unique_months = [list(unique_months.iloc[i]) for i in range(unique_months.shape[0])]
unique_months = [datetime(year=t[0],month=t[1],day=t[2]) for t in unique_months]

import matplotlib.cbook as cbook
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

ax = plt.gca()
ax.tick_params(which="major",pad=10)
ax.tick_params(which="minor",pad=40)
#ax.xaxis.set_major_locator(mdates.ConsizeDateFormatter(ax.xaxis.get_major_locator()))
# 16 is a slight approximation since months differ in number of days.
ax.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=16))

ax.xaxis.set_major_formatter(dates.DateFormatter('%d'))
ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))

for tick in ax.xaxis.get_minor_ticks():
    tick.tick1line.set_markersize(0)
    tick.tick2line.set_markersize(0)
    tick.label1.set_horizontalalignment('center')
    tick.label1.set_verticalalignment('center')
#plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))

shown_times = [0,3,6,9,12,15,18,21,24]
plt.gca().set_yticks(ticks=shown_times,labels=shown_times)

plt.ylabel("hour of day")
plt.xlabel("date",labelpad=10)

plt.savefig("fig.png",dpi=300)
plt.close()
# %%
