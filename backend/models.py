import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import database as _database


class Station(_database.Base):
    __tablename__ = "stations"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    code = _sql.Column(_sql.String, unique=True, index=True)
    name = _sql.Column(_sql.String, unique=False)

    param = _orm.relationship("Parameter", back_populates="owner")


class Parameter(_database.Base):
    __tablename__ = "parameters"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    station_id = _sql.Column(_sql.Integer, _sql.ForeignKey("stations.id"))
    name = _sql.Column(_sql.String, index=True)
    code = _sql.Column(_sql.String, index=True)

    owner = _orm.relationship("Station", back_populates="param")
