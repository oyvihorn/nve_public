from typing import Dict  # Import typing modules for static type check
import fastapi as _fastapi
from fastapi import HTTPException

from dotenv import load_dotenv

# from fastapi import HTTPException
import schemas
import services
import database

import sqlalchemy.orm as _orm

from fastapi.middleware.cors import CORSMiddleware

"""
TODO:
Implement asynchronous call
Implement authorization and authentication
Option: Docker run with db docker-compose with redis/mem cach
Web hooks - could trigger update of database
New/deleted stations, probably not, possible collisions. Mixing responsibility
HTTPExceptions handling in frontend - so far they are bypassed. Do similar as for timeseries exceptions.
Finalize pvc or similar for daily update
Sort list of stations
Services module to extensive, split.
Improve tests

Automation functions for apis, hlook at implemtation?
Look into Slowapi
"""

app = _fastapi.FastAPI()
database.create_database()

"""
Needed in order to populate Station-parameter database
"""
URL_STATIONS = "https://hydapi.nve.no/api/v1/Stations"
URL_PARAMETERS = "https://hydapi.nve.no/api/v1/Parameters"
URL_SERIES = "https://hydapi.nve.no/api/v1/Series"
FC_NAME = "nve_observasjoner_raw"
FC_NAME_FINAL = "nve_observasjoner"

"""
Load environment variables from .env
NB: When this is run from a container then this is not needed, use the app.env file instead.
"""
load_dotenv()

"""
Populate database with stations and parameters
This part will be in a cron job that updates stations and parameter db daily.
Not to be run for every app instance. Only observations needs to be pulled from api every time.
Stations and parameters are fetched from db for every selection done in front end pull down menus as it
needs to filter parameters based on stations selected and vice versa.
"""
# from populate_db import stations_db
# stations_db(URL_STATIONS)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/stations")
def stations(
    station_obj: schemas.ParametersOnly,
    db: _orm.Session = _fastapi.Depends(database.get_db),
) -> Dict[str, str]:
    all_stations = services.get_stations(station_obj.parameter, db)
    if all_stations == {}:
        raise HTTPException(
            status_code=400, detail=str("List of stations not returned from db")
        )
    return all_stations


@app.post("/api/parameters", response_model=dict)
def parameters(
    station_obj: schemas.StationBase,
    db: _orm.Session = _fastapi.Depends(database.get_db),
) -> Dict[str, int]:
    all_params = services.get_parameters(station_obj.station, db)
    if all_params == {}:
        raise HTTPException(
            status_code=400, detail=str("List of parameters not returned from db")
        )
    return all_params


@app.get("/api/parameters_all")
def parameters_all(
    db: _orm.Session = _fastapi.Depends(database.get_db),
) -> Dict[str, int]:
    all_params = services.get_parameters_all(db)
    if all_params == {}:
        raise HTTPException(
            status_code=400, detail=str("List of parameters not returned from db")
        )
    return all_params


@app.get("/api/stations_all")
def stations_all(
    db: _orm.Session = _fastapi.Depends(database.get_db),
) -> Dict[str, str]:
    all_params = services.get_stations_all(db)
    if all_params == {}:
        raise HTTPException(
            status_code=400, detail=str("List of stations not returned from db")
        )
    return all_params


@app.get("/api/timerange")
def all_timerange() -> Dict[str, str]:
    timerange = {"P1D/": "1 Day", "P2D/": "2 Days", "P3D/": "3 Days", "P7D/": "1 Week"}
    return timerange


@app.post("/api/series")
def series(
    station_obj: schemas.StationCreate,
    db: _orm.Session = _fastapi.Depends(database.get_db),
):
    """
    Error handling for this function is handled in the service part of the code.
    Meaning plot is always returned, but could contain error string if no obs exist.
    """
    return services.create_plot(station_obj, db)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "NVE Sensor API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
