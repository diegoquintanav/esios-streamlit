import typing as T
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy import fft

PATH_DATA = Path(__file__).parent.joinpath("data", "data.csv")


@st.cache
def read_csv(path: T.Optional[Path]) -> pd.DataFrame:

    # format index
    df = pd.read_csv(path)
    df.index = pd.to_datetime(df["datetime"])

    # drop unnecesary columns
    df = df[["value"]]

    return df


def plot_time(df: pd.DataFrame) -> T.Tuple[plt.Figure, plt.Axes]:
    # plot data
    fig, ax = plt.subplots(figsize=(20, 10))
    df["value"].plot(ax=ax, color="red")

    # format axis
    ax.set_xlabel("Time [s]", size=20)
    ax.set_ylabel("Amplitude [MW]", size=20)

    # format y axis to show MW
    # https://matplotlib.org/stable/gallery/ticks/tick-formatters.html
    ax.yaxis.set_major_formatter(lambda x, pos: str(x / 1000.0))

    ax.grid()

    return fig, ax

@st.cache
def compute_fft(df: pd.DataFrame) -> np.ndarray:
    return fft.fft(df["value"].values)


def plot_frequency(df: pd.DataFrame) -> T.Tuple[plt.Figure, plt.Axes]:
    # https://stackoverflow.com/questions/6363154/what-is-the-difference-between-numpy-fft-and-scipy-fftpack
    # compute the 1D fast fourier transform
    fft_values = compute_fft(df)

    # compute human-readable frequencies
    freqs_in_fft = np.arange(0, len(fft_values))
    n_samples = len(df["value"])

    # divide the time in proportional units
    # we have 34 days, sampled with 10 minute resolution
    # we want to express this time in days of a year

    # map data to a single year
    # a day has 24 hours
    # each hour has 6 10-minute spans
    # a year has 365.25 of these
    t_units_per_year = 24 * 6 * 365.2524  # number of 10-minute spans in a year

    # how many years are being expressed currently in out dataset?
    # result should be similar to 34/365.2524
    years_per_dataset = n_samples / (t_units_per_year)

    # hoy many frequencies can be allocated in a single year?
    freqs_per_year = freqs_in_fft / years_per_dataset

    # plot results
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.step(freqs_per_year, np.abs(fft_values), where="pre")

    # format
    ax.set_xscale("log")
    ax.set_yscale("log")

    ticks = [1, 365.2524, 365.2524 * 24, 365.2524 * 24 * 6]
    labels = ["1/Year", "1/day", "1/hour", "1/10min"]

    ax.vlines(ticks, *ax.get_ylim(), "g", label=labels, alpha=0.2, linewidth=10)

    for tick, label in zip(ticks, labels):
        ax.text(
            x=tick * 0.75, y=ax.get_ylim()[1] * 0.075, s=label, size=20, rotation=90
        )

    ax.set_xlabel("Frequency [Hz] (log scale)", size=20)
    ax.set_ylabel("Amplitude (log scale)", size=20)

    ax.grid()

    return fig, ax


df = read_csv(PATH_DATA)

st.title("Daily aggregated demand in Spain")

st.header("About")

# github
st.write(
    """Plots of the daily aggregated demand in Spain between 2018/09/02 and 2018/10/06 in time and frequency domain. 
    
Find the original repo in [github](https://github.com/diegoquintanav/esios-streamlit). 
The data was obtained from [Red eléctrica de España](https://www.esios.ree.es/es/analisis/1293?vis=1&start_date=02-09-2018T00%3A00&end_date=06-10-2018T23%3A50&compare_start_date=01-09-2018T00%3A00&groupby=minutes10&level=1&zoom=6&latlng=40.91351257612758,-1.8896484375) 
and downloaded using their [API service](https://api.esios.ree.es/).

The query issued used for this visualization is

```
https://api.esios.ree.es/indicators/1293?locale=es&start_date=2018-09-02T00%3A00%3A00&end_date=2018-10-06T23%3A00%3A00&time_agg=sum&time_trunc=ten_minutes
```
"""
)

st.subheader("Time domain")
fig, ax = plot_time(df)
st.pyplot(fig)

st.subheader("Frequency domain")
fig, ax = plot_frequency(df)
st.pyplot(fig)

st.subheader("Data")
st.dataframe(df)
