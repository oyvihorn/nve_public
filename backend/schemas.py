from pydantic import BaseModel


class StationBase(BaseModel):
    station: str


class StationCreate(StationBase):
    station2: str
    station3: str
    parameter: str
    parameter2: str
    timerange: str
    plottype: str


class ParametersOnly(BaseModel):
    parameter: str


class StationDB(BaseModel):
    id: int
    name_st: str
    code_st: str

    class Config:
        orm_mode = True


class ParameterDB(BaseModel):
    id: int
    station_id: str
    name_para: str
    code_para: str

    class Config:
        orm_mode = True
