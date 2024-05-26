from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import pandas as pd
import plotly.express as px  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
from plotly.graph_objs import Figure  # type: ignore
import plotly as pt  # type: ignore

import sqlalchemy.orm as _orm
import schemas
import models
from api import api_call


class Plot(ABC):
    def __init__(
        self,
        all_params: str,
        stations: List[str],
        db: _orm.Session,
        station_obj: schemas.StationCreate,
    ):
        self.all_params = all_params
        self.stations = stations
        self.db = db
        self.station_obj = station_obj

    def fetch_series(self):
        self.station_names = get_station_name(self.stations, self.db)
        return get_series(self.stations, self.all_params, self.station_obj.timerange)

    @abstractmethod
    def create_fig(self, observation_list: List[Dict[str, Any]]) -> Figure | None:
        pass


class StationsCompare(Plot):

    def create_fig(self, observation_list: List[Dict[str, Any]]) -> Figure | None:
        inc = 0
        fig = make_subplots(
            rows=len(observation_list),
            cols=1,
            subplot_titles=([str(x) for x in self.station_names]),
        )
        parameters_name = []
        for station in observation_list:
            _ = station.pop("stationId")
            if not station:
                inc += 1
                continue
            df_series = create_dataframe(station)
            parameters, parameters_name = parameters_get_name(df_series)
            # check if station is missing parameters.
            if len(set(parameters)) < 0:
                return None
            inc += 1
            line_plot_param(fig, df_series, parameters, inc)
        fig: Figure = fig.update_layout(  # type: ignore difficult to type check update_layout
            height=(100 + (200 * len(observation_list))),
            width=900,
            title_text=f"Stations compared for {parameters_name[0]}",
            template="seaborn",
        )
        return fig


class ParametersCompare(Plot):

    def create_fig(self, observation_list: List[Dict[str, Any]]) -> Figure | None:
        fig = None
        for station in observation_list:
            _ = station.pop("stationId")
            df_series: pd.DataFrame = create_dataframe(station, "orient")
            df_series = df_series.transpose()  # type: ignore # transpose unknown part type
            parameters, parameters_name = parameters_get_name(df_series)
            # check if parameters are the same or missing. Should not be necessary.
            if len(set(parameters)) < 2:
                return None
            """ jointplot """
            fig = scatter_plot(df_series, parameters, parameters_name)
        return fig


class ParameterMatrix(Plot):

    def create_fig(self, observation_list: List[Dict[str, Any]]) -> Figure | None:
        fig = None
        for station in observation_list:
            _ = station.pop("stationId")
            df_series = create_dataframe(station, "orient")
            df_series = df_series.transpose()  # type: ignore # transpose unknown part type
            fig = scatter_matrix(df_series)
        return fig


class ParametersAll(Plot):

    def create_fig(self, observation_list: List[Dict[str, Any]]) -> Figure | None:
        parameters = []
        for station in observation_list:
            _ = station.pop("stationId")
            df_series = create_dataframe(station, "orient")
            df_series = df_series.transpose()  # type: ignore # transpose unknown part type
            parameters = [str(x) for x in df_series.columns if x.endswith("value")]
            inc = 0
            fig = make_subplots(
                rows=len(parameters),
                cols=1,
                subplot_titles=([str(x).strip("_value") for x in parameters]),
            )
            for para in parameters:
                inc += 1
                line_plot_station(fig, df_series, para, inc)
        fig: Figure = fig.update_layout(  # type: ignore difficult to type check update_layout
            height=(100 + (200 * len(parameters))),
            width=900,
            title_text=f"All parameters for {self.station_names[0]}",
            template="seaborn",
        )
        return fig


def line_plot_param(
    fig: Figure, df_series: pd.DataFrame, parameters: List[str], inc: int
) -> Figure:
    return fig.append_trace(  # type: ignore
        px.line(  # type: ignore
            df_series, x=f"{parameters[0]}_time", y=parameters[0], markers=True
        )["data"][0],
        row=inc,
        col=1,
    )


def scatter_plot(
    df_series: pd.DataFrame, parameters: List[str], parameters_name: List[str]
):
    return px.scatter(  # type: ignore
        df_series,
        x=f"{parameters[0]}",
        y=f"{parameters[1]}",
        marginal_y="histogram",
        marginal_x="histogram",
        template="seaborn",
        title=f"Comparing {parameters_name[0]} and {parameters_name[1]}",
        height=750,
        width=750,
    )


def scatter_matrix(df_series: pd.DataFrame):
    return px.scatter_matrix(  # type: ignore
        df_series[[str(x) for x in df_series.columns if x.endswith("value")]],
        template="seaborn",
        title="Matrix compare of all parameters",
        width=900,
        height=900,
    )


def line_plot_station(
    fig: Figure, df_series: pd.DataFrame, para: str, inc: int
) -> Figure:
    return fig.append_trace(  # type: ignore
        px.line(df_series, x=f"{para}_time", y=para, markers=True)["data"][0],  # type: ignore
        row=inc,
        col=1,
    )


def create_dataframe(station: Dict[str, Any], index: str = "None") -> pd.DataFrame:
    if index == "orient":
        return pd.DataFrame.from_dict(station, orient="index")
    else:
        return pd.DataFrame.from_dict(station)


def parameters_get_name(df_series: pd.DataFrame) -> Tuple[List[str], List[str]]:
    parameters = [str(x) for x in df_series.columns if x.endswith("value")]
    parameters_name = [
        str(x).strip("_value") for x in df_series.columns if x.endswith("value")
    ]
    return parameters, parameters_name


def get_station_name(station_id: List[str], db: _orm.Session) -> List[str]:
    station_unique: List[str] = []
    for id in station_id:
        st_name = (
            db.query(models.Station.name).filter(models.Station.code == id).first()
        )
        if st_name:
            station_unique.append(st_name[0])

    if station_unique:
        return station_unique
    else:
        return []


def get_observation_url(station: str, parameter: str, reference_time: str) -> str:
    return f"https://hydapi.nve.no/api/v1/Observations?StationId={station}&Parameter={parameter}&ResolutionTime=0&ReferenceTime={reference_time}"


def get_series(
    stations: List[str], parameters: str, reference_time: str = "P2D/"
) -> List[Dict[str, Any]]:

    def pop_obs(name: str, value: float | str) -> None:
        if name not in obs:
            obs[name] = []
        obs[name].append(value)

    def pop_observations(observations: Dict[str, Any]) -> None:
        for observation in observations["data"]:
            obs["stationId"] = observation.get("stationId")
            param_name_value_time = f"{observation.get('parameterName')}_value_time"
            param_name_value = f"{observation.get('parameterName')}_value"

            if observation.get("observations"):
                for timeseries in observation.get("observations"):
                    if timeseries.get("value"):
                        param_value = float(timeseries.get("value"))
                        param_value_time: str = timeseries.get("time")
                        pop_obs(param_name_value, param_value)
                        pop_obs(param_name_value_time, param_value_time)

    observation_list: List[Dict[str, Any]] = []
    previous_station = None

    for station in stations:
        if previous_station is not None and station == previous_station:
            continue
        observation_url = get_observation_url(station, parameters, reference_time)
        observations = api_call(observation_url)
        if not observations:
            # implement logging
            # somelogger(f"could not find observation for {station}")
            continue
        obs: Dict[str, Any] = {}
        pop_observations(observations)
        if obs:
            observation_list.append(obs)
        previous_station = station

    return observation_list


def set_error_string() -> str | None:
    graphJSON: str | None = pt.io.to_json(  # type: ignore
        px.line(template="seaborn", title="No data returned from API"), pretty=True  # type: ignore
    )
    return graphJSON
