from typing import Any, Dict
import schemas
import sqlalchemy.orm as _orm

import plotly as pt  # type: ignore
import plottypes
import models


def get_stations(parameter: str, db: _orm.Session) -> Dict[str, Any]:
    st_id = (
        db.query(models.Station.name, models.Station.code)
        .join(models.Parameter, models.Station.id == models.Parameter.station_id)
        .filter(models.Parameter.code == parameter)
        .all()
    )
    station_unique: Dict[str, Any] = {}
    for name, code in st_id:
        station_unique[name] = code
    return station_unique


def get_parameters(station: str, db: _orm.Session) -> Dict[str, Any]:
    st_id = (
        db.query(models.Parameter.name, models.Parameter.code)
        .join(models.Station, models.Parameter.station_id == models.Station.id)
        .filter(models.Station.code == station)
        .all()
    )
    parameter_unique: Dict[str, Any] = {}
    for name, code in st_id:
        parameter_unique[name] = code
    return parameter_unique


def get_parameters_all(db: _orm.Session) -> Dict[str, Any]:
    st_id = db.query(models.Parameter.name, models.Parameter.code).all()
    parameter_unique: Dict[str, Any] = {}
    for name, code in st_id:
        parameter_unique[name] = code
    return parameter_unique


def get_stations_all(db: _orm.Session) -> Dict[str, Any]:
    st_id = db.query(models.Station.name, models.Station.code).all()
    station_unique: Dict[str, Any] = {}
    for name, code in st_id:
        station_unique[name] = code
    return station_unique


def create_plot(station_obj: schemas.StationCreate, db: _orm.Session):
    if station_obj.plottype == "Stations compare":
        return populate_plot(
            plottypes.StationsCompare(
                station_obj.parameter,
                [station_obj.station, station_obj.station2, station_obj.station3],
                db,
                station_obj,
            )
        )
    elif station_obj.plottype == "Parameters compare":
        all_params = ",".join([station_obj.parameter, station_obj.parameter2])
        return populate_plot(
            plottypes.ParametersCompare(
                all_params,
                [station_obj.station],
                db,
                station_obj,
            )
        )
    elif station_obj.plottype == "Parameter matrix":
        all_params = ",".join(
            [str(value) for value in get_parameters(station_obj.station, db).values()]
        )
        return populate_plot(
            plottypes.ParameterMatrix(
                all_params,
                [station_obj.station],
                db,
                station_obj,
            )
        )
    elif station_obj.plottype == "Parameters all":
        all_params = ",".join(
            [str(value) for value in get_parameters(station_obj.station, db).values()]
        )
        return populate_plot(
            plottypes.ParametersAll(
                all_params,
                [station_obj.station],
                db,
                station_obj,
            )
        )


def populate_plot(station_obj: plottypes.Plot):
    observation_list = station_obj.fetch_series()
    if not observation_list:
        return plottypes.set_error_string()
    fig = station_obj.create_fig(observation_list)
    if not fig:
        return plottypes.set_error_string()
    graphJSON: str | None = pt.io.to_json(fig, pretty=True)  # type: ignore # todo type safe return to_json
    return graphJSON
