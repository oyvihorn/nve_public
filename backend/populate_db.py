from typing import Dict, List, Any
import schemas
import models
import database
import sqlalchemy.orm as _orm
from api import api_call


def all_station_params(stations: Dict[str, Any] | None, db: _orm.Session):
    unique_station: set[str] = set()
    if stations:
        station_list: List[Any] = stations["data"]

        for station in station_list:
            station_db = schemas.StationDB
            station_db.name_st = station["stationName"]
            station_db.code_st = station["stationId"]
            if station_db.code_st not in unique_station:
                populate_db_station(station_db, db)
            for param in station["seriesList"]:
                param_db = schemas.ParameterDB
                param_db.name_para = param["parameterName"]
                param_db.code_para = param["parameter"]
                populate_db_parameter(station_db, param_db, db)

            unique_station.add(station_db.code_st)


def populate_db_station(station_db: schemas.StationDB, db: _orm.Session):
    # create dict of pydantic model
    # user_dict = station_db.dict()
    # vice versa
    # backtoSchema = schemas.StationDB(**user_dict)
    stat = models.Station(name=station_db.name_st, code=station_db.code_st)
    db.add(stat)
    db.commit()
    db.refresh(stat)


def populate_db_parameter(
    station_db: schemas.StationDB,
    param_db: schemas.ParameterDB,
    db: _orm.Session,
):
    st: models.Station = (
        db.query(models.Station).filter_by(name=station_db.name_st).first()
    )
    param = models.Parameter(
        name=param_db.name_para, code=param_db.code_para, station_id=st.id
    )
    db.add(param)
    db.commit()
    db.refresh(param)


def stations_db(url_stations: str):
    database.backup_db()
    stations = api_call(url_stations)
    db_gen = database.get_db()
    db = next(db_gen)
    return all_station_params(stations, db)
