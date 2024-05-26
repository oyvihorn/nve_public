from typing import Any, Dict
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session, sessionmaker
import sqlalchemy as sql
from main import app
from database import get_db, Base
from populate_db import all_station_params
from api import api_call
from plottypes import set_error_string, get_station_name

DATABASE_URL = "sqlite:///:memory:.db"
engine = sql.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=sql.StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ovveride_get_db():
    """
    This will override the get_db function in the main.py file so that we use in-memory
    database for testing instead of overwriting the database file.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = ovveride_get_db

client = TestClient(app)


# def setup():
#     return Base.metadata.create_all(bind=engine)


# def teardown():
#     return Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db():
    """
    Populate the database with test data, only 2 records.
    Create a session for the test database and populate and yield
    this to test functions. Drop database when test flow is done.
    Remember to check that no function is triggering the get_db function
    in main.py as this will create a production test version of the database!
    TO DO: Improve on stations import. For now read 2 first records dynamiccaly:
    should match: {'Femsjø': '1.15.0', 'Lierelv': '1.200.0'}.
    Split route and db tests.
    improve exception seperation for route and services.
    """

    def data_exists(stations: Dict[str, Any] | None) -> None:
        if not stations:
            raise ValueError("No stations returned from API")

    Base.metadata.create_all(bind=engine)
    db_gen = ovveride_get_db()
    db = next(db_gen)
    for station_name in ["Femsjø", "Lierelv"]:
        url_stations: str = (
            f"https://hydapi.nve.no/api/v1/Stations?StationName={station_name}"
        )
        stations: Dict[str, Any] | None = api_call(url_stations)
        data_exists(stations)
        stations["data"] = stations["data"][0:2]

        all_station_params(stations, db)
    yield db
    Base.metadata.drop_all(bind=engine)


def test_api_call_fail():
    response = api_call("http://dontexisturl.com")

    assert response is None


def test_get_station_name_fail(db: Session):
    name = get_station_name(["9.99.9"], db)

    assert name == []


def test_root(db: Session):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NVE Sensor API"}


def test_stations_all(db: Session):
    response = client.get("api/stations_all")

    assert response.status_code == 200
    assert response.json() == {"Femsjø": "1.15.0", "Lierelv": "1.200.0"}


def test_parameters_all(db: Session):
    response = client.get("api/parameters_all")

    assert response.status_code == 200
    assert response.json() == {
        "Vannstand": 1000,
        "Magasinvolum": 1004,
        "Vannføring": 1001,
        "Vanntemperatur": 1003,
    }


def test_stations_fail(db: Session):
    response = client.post("api/stations", json={"parameter": 99999999})

    assert response.status_code == 400
    assert response.json() == {"detail": "List of stations not returned from db"}


def test_parameters_fail(db: Session):
    response = client.post("api/parameters", json={"station": "9.99.9"})

    assert response.status_code == 400
    assert response.json() == {"detail": "List of parameters not returned from db"}


def test_stations_ok(db: Session):
    response = client.post("api/stations", json={"parameter": 1000})

    assert response.status_code == 200
    assert response.json() == {"Femsjø": "1.15.0", "Lierelv": "1.200.0"}


def test_parameters_ok(db: Session):
    response = client.post("api/parameters", json={"station": "1.15.0"})

    assert response.status_code == 200
    assert response.json() == {"Vannstand": "1000", "Magasinvolum": "1004"}


def test_timerange():
    response = client.get("api/timerange")

    assert response.status_code == 200
    assert response.json() == {
        "P1D/": "1 Day",
        "P2D/": "2 Days",
        "P3D/": "3 Days",
        "P7D/": "1 Week",
    }


def test_series_stations_compare_fail(db: Session):
    response = client.post(
        "api/series",
        json={
            "station": "1.15.0",
            "station2": "1.15.0",
            "station3": "1.200.0",
            "parameter": "99999999",
            "parameter2": "99999999",
            "timerange": "P1D/",
            "plottype": "Stations compare",
        },
    )

    assert response.status_code == 200
    assert response.json() == set_error_string()


def test_series_parameters_all_fail(db: Session):
    response = client.post(
        "api/series",
        json={
            "station": "9.99.9",
            "station2": "9.99.9",
            "station3": "9.99.9",
            "parameter": "1000",
            "parameter2": "1004",
            "timerange": "P1D/",
            "plottype": "Parameters all",
        },
    )

    assert response.status_code == 200
    assert response.json() == set_error_string()


def test_series_parameters_all_ok(db: Session):
    response = client.post(
        "api/series",
        json={
            "station": "1.15.0",
            "station2": "1.15.0",
            "station3": "1.200.0",
            "parameter": "1000",
            "parameter2": "1004",
            "timerange": "P1D/",
            "plottype": "Parameters all",
        },
    )

    assert response.status_code == 200
    assert response.json() != set_error_string()


def test_series_parameters_compare(db: Session):
    response = client.post(
        "api/series",
        json={
            "station": "1.15.0",
            "station2": "1.15.0",
            "station3": "1.200.0",
            "parameter": "1000",
            "parameter2": "1004",
            "timerange": "P1D/",
            "plottype": "Parameters compare",
        },
    )

    assert response.status_code == 200
    assert response.json() != set_error_string()


def test_series_parameters_compare_fail(db: Session):
    response = client.post(
        "api/series",
        json={
            "station": "9.99.9",
            "station2": "1.15.0",
            "station3": "1.200.0",
            "parameter": "1000",
            "parameter2": "1004",
            "timerange": "P1D/",
            "plottype": "Parameters compare",
        },
    )

    assert response.status_code == 200
    assert response.json() == set_error_string()


def test_series_parameters_matrix(db: Session):
    response = client.post(
        "api/series",
        json={
            "station": "1.15.0",
            "station2": "1.15.0",
            "station3": "1.200.0",
            "parameter": "1000",
            "parameter2": "1004",
            "timerange": "P1D/",
            "plottype": "Parameter matrix",
        },
    )

    assert response.status_code == 200
    assert response.json() != set_error_string()


def test_series_stations_compare(db: Session):
    response = client.post(
        "api/series",
        json={
            "station": "1.15.0",
            "station2": "1.15.0",
            "station3": "1.200.0",
            "parameter": "1000",
            "parameter2": "1004",
            "timerange": "P1D/",
            "plottype": "Stations compare",
        },
    )

    assert response.status_code == 200
    assert response.json() != set_error_string()
