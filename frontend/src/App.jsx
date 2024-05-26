import React, { useState, useEffect } from 'react';
import './App.css';
import Scatter from "./Scatter"
import ErrorMessage from "./ErrorMessage";

const App = () => {
  const [errorMessage, setErrorMessage] = useState("");
  const [plot, setPlot] = useState("[]");
  const [station, setStation] = useState("12.534.0");
  const [station2, setStation2] = useState("12.193.0");
  const [station3, setStation3] = useState("12.192.0");
  const [parameter, setParameter] = useState("1000");
  const [parameter2, setParameter2] = useState("1001");
  const [timerange, setTimerange] = useState("P1D/");
  const [plottype, setPlottype] = useState("Parameters all");
  const [stations, setStations] = useState([]);
  const [parameters, setParameters] = useState([]);
  const [timeranges, setTimeranges] = useState([]);
  const [plottypes, setPlottypes] = useState(["Parameters all", "Parameters compare", "Parameter matrix", "Stations compare"]);


  const getTimeseries = async () => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ station: station, station2: station2, station3: station3, parameter: parameter, parameter2: parameter2, timerange: timerange, plottype: plottype }),
    };

    const response = await fetch(`/api/series`, requestOptions);

    const data = await response.json();
    if (!response.ok) {
      console.log("something messed up");
    } else {
    console.log("series")
    setPlot(data);
    }
  }

  const initializeStations = async (parameter) => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parameter: parameter }),
    };
    const response = await fetch(`/api/stations`, requestOptions);
    const data = await response.json();
    setStations(data);
  } 

  const initializeParameters = async (station) => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ station: station}),
    };
    const response = await fetch(`/api/parameters`, requestOptions);
    const data = await response.json();
    setParameters(data);
  }

  const initializeAllParameters = async () => {
    const requestOptions = {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    };
    const response = await fetch(`/api/parameters_all`, requestOptions);
    const data = await response.json();
    setParameters(data);
  }

  const initializeAllStations = async () => {
    const requestOptions = {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    };
    const response = await fetch(`/api/stations_all`, requestOptions);
    const data = await response.json();
    setStations(data);
  }

  const initializeTimerange = async () => {
    const requestOptions = {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    };
    const response = await fetch(`/api/timerange`, requestOptions);
    const data = await response.json();
    setTimeranges(data);
  }

  useEffect(() => {
    initializeStations(parameter);
    initializeParameters(station);
    initializeTimerange();
    console.log(parameters)
  }, []);

  useEffect(() => {
    if (plottype == 'Stations compare'){
      initializeStations(parameter);
    }
  }, [parameter]);

  useEffect(() => {
    if (plottype != 'Stations compare'){
      initializeParameters(station);
    }
  }, [station]);

  useEffect(() => {
    if (plottype == 'Stations compare'){
      initializeAllParameters();
      setParameter("1001")
    }
    else {
      initializeAllStations();
      initializeParameters(station);
    }
  }, [plottype]);

  const handleSubmit = (e) => {
    e.preventDefault()
    getTimeseries();
  };

  return (
    <div className="App">
      <header className="App-header">
        Tidsserier for NVE målestasjoner 
      </header>
      <div className="App-body">
      <ErrorMessage message={errorMessage} />
      <section className="section">
      <div className="container">
      <div className="columns">
        <div className="column is-one-quarter">
        <form className="box" onSubmit={handleSubmit}>
        <h1 className="title is-5 has-text-centered has-text-link">Select series to plot</h1>

        <div className="field">
        <label className="label">Plot type</label>
        <div className="control">       
          <div className="select">
            <select value={plottype} onChange={(e) => setPlottype(e.target.value)}>
            {plottypes.map((type) => (
              <option>{type}</option>
            ))}
            </select>
          </div>
          </div>
          </div>

        <div className="field">
        <label className="label">Select station</label>
        <div className="control">       
          <div className="select">
            <select value={station} onChange={(e) => setStation(e.target.value)}>
            {Object.entries(stations).map(([key, value]) => (
              <option value={value}>{key}</option>
            ))}
            </select>
          </div>
          </div>
          </div>
          { plottype === 'Stations compare' ? 
          <div className="field">
        <label className="label">Select station 2</label>
        <div className="control">       
          <div className="select">
            <select value={station2} onChange={(e) => setStation2(e.target.value)}>
            {Object.entries(stations).map(([key, value]) => (
              <option value={value}>{key}</option>
            ))}
            </select>
          </div>
          </div>
          </div>
          : null
        } 

          { plottype === 'Stations compare' ? 
          <div className="field">
          <label className="label">Select station 3</label>
          <div className="control">       
          <div className="select">
            <select value={station3} onChange={(e) => setStation3(e.target.value)}>
            {Object.entries(stations).map(([key, value]) => (
              <option value={value}>{key}</option>
            ))}
            </select>
          </div>
          </div>
          </div>
          : null
        } 

        <div className="field">
        <label className="label">Select parameter</label>
        <div className="control">       
          <div className="select">
            <select value={parameter} onChange={(e) => setParameter(e.target.value)}>
            {Object.entries(parameters).map(([key, value]) => (
              <option value={value}>{key}</option>
            ))}
            </select>
          </div>
          </div>
          </div>

        { plottype === 'Parameters compare' ? 
          <div className="field">
          <label className="label">Select parameter 2</label>
          <div className="control">       
          <div className="select">
            <select value={parameter2} onChange={(e) => setParameter2(e.target.value)}>
            {Object.entries(parameters).map(([key, value]) => (
              <option value={value}>{key}</option>
            ))}
            </select>
          </div>
          </div>
          </div>
          : null
        } 

        <div className="field">
        <label className="label">Time range</label>
        <div className="control">       
          <div className="select">
            <select value={timerange} onChange={(e) => setTimerange(e.target.value)}>
            {Object.entries(timeranges).map(([key, value]) => (
              <option value={key}>{value}</option>
            ))}
            </select>
          </div>
          </div>
          </div>

        <div className="field is-grouped is-grouped-centered m-4">
          <div className="control">
            <button type="submit" className="button is-link">Submit</button>
          </div>
          <div className="control">
            <button className="button is-link is-light">Cancel</button>
          </div>
        </div>

          </form>
        </div>
        <div className="column is-three-quarters">
          <Scatter data={plot}/>
        </div>
      </div>
      
      </div>
  </section>
  </div >
    </div>
  );
}

export default App;
