import datetime as dt
import json
import os
from pathlib import Path

import pandas as pd
from pandas.core.dtypes import base
import requests

BASE_URL = os.getenv("BASE_URL", "https://api.esios.ree.es")


class UnconfiguredEnvironment(Exception):
    """base class for Missing environment variables"""

    pass


# sane check for authorization token
try:
    PERSONAL_TOKEN = os.getenv("ESIOS_TOKEN")
except KeyError as e:
    raise UnconfiguredEnvironment("PERSONAL_TOKEN environment variable not set")


def make_request(request_id: str, params: dict) -> requests.Response:
    """issues a GET request to esios rest API

    Retrieves data from a particular period in time

    Args:
        request_id (str): id of the resource in the esios databases.
        params (dict): arguments in the request. See <https://api.esios.ree.es/indicator/getting_a_disaggregated_indicator_filtering_values_by_a_date_range_and_geo_ids,_grouped_by_geo_id_and_month,_using_avg_aggregation_for_geo_and_avg_for_time_without_time_trunc> for details

    Returns:
        requests.Response: a response object.
    """
    # define the headers of the request
    headers = {
        "Accept": "application/json; application/vnd.esios-api-v1+json",
        "Content-Type": "application/json",
        "Host": "api.esios.ree.es",
        "Authorization": "Token token={}".format(PERSONAL_TOKEN),
        "Cookie": "",
    }

    # base url of the request
    INDICATOR_URL = BASE_URL + f"/indicators/{request_id}"

    # make the request
    r = requests.get(INDICATOR_URL, headers=headers, params=params)

    return r


def persist_data(r: requests.Response) -> pd.DataFrame:
    """Manipulates request and persist results on disk

    Saves complete JSON file and a subset of values in CSV format.

    Args:
        r (requests.Response): a query response object

    Returns:
        pd.DataFrame: a dataframe of the subset extracted from the JSON response
    """

    basepath = Path(__file__).parent.joinpath("data")
    basepath.mkdir(exist_ok=True)

    # save to json
    with open(basepath.joinpath("dump.json"), "wt") as fp:
        json.dump(r.json(), fp)

    # let the method fail with KeyError explicitly
    r_values = r.json()["indicator"]["values"]

    # save as csv
    df = pd.DataFrame(r_values)
    df.to_csv(basepath.joinpath("data.csv"))

    return df

if __name__ == "__main__":

    id_request = "1293"

    # define the parameters of the request
    params = {
        "locale": "es",
        # "datetime": A certain date to filter values by (iso8601 format)
        "start_date": dt.datetime(
            year=2018, month=9, day=2, hour=0, minute=0, second=0
        ).isoformat(),  # Beginning of the date range to filter indicator values (iso8601 format)
        "end_date": dt.datetime(
            year=2018, month=10, day=6, hour=23, minute=0, second=0
        ).isoformat(),  # End of the date range to filter indicator values (iso8601 format)
        "time_agg": "sum",  # How to aggregate indicator values when grouping them by time. Accepted values: `sum`, `average`. Default value: `sum`.
        "time_trunc": "ten_minutes",  # Tells the API how to trunc data time series. Accepted values: `ten_minutes`, `fifteen_minutes`, `hour`, `day`, `month`, `year`.
        # "geo_agg": None, # How to aggregate indicator values when grouping them by geo_id. Accepted values: `sum`, `average`. Default value: `sum`.
        # "geo_ids": None, # Tells the API the geo ids to filter the dataear && ./bin/rspec by.
        # "geo_trunc": None, # Tells the API how to group data at geolocalization level when the geo_agg is informed. Accepted values: 'country', 'electric_system', 'autonomous_community', 'province', 'electric_subsystem', 'town' and 'drainage_basin'
    }

    r = make_request(id_request, params)
    persist_data(r)
