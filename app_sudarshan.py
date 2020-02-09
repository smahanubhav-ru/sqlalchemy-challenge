import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Routes
app = Flask(__name__)

@app.route("/")
def welcome():
    """List of all the available routes."""
    return (
        f"<h1>Welcome to home page.</h1><br/>"
        f"<h3>Available Routes:</h3><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start_date/end_date<br/>"        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON representation of dictionary using date as the key and prcp as the value."""
    year_before = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    data_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_before).order_by(Measurement.date).all()
    prcp_dict = {date: prcp for date, prcp in data_scores}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    all_stations = session.query(Station.station).all()
    all_stations_list = list(np.ravel(all_stations))
    return jsonify(all_stations_list)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    year_before = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_query = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_before).order_by(Measurement.date).all()
    tobs_list = list(np.ravel(tobs_query))
    return jsonify(tobs_list)


@app.route("/api/v1.0/temp/<start_dt>")
def start_only(start_dt):
    """Return TMIN, TAVG, TMAX for all dates greater than and equal to the start date."""
    agg_func = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    agg_query = session.query(*agg_func).filter(Measurement.date >= start_dt).all()
    agg_list = list(np.ravel(agg_query))
    return jsonify(agg_list)

@app.route("/api/v1.0/temp/<start_dt>/<end_dt>")
def start_end(start_dt=None, end_dt=None):
    """Return TMIN, TAVG, TMAX for dates between the start and end date inclusive."""
    agg_func = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    agg_query = session.query(*agg_func).filter(Measurement.date >= start_dt).\
        filter(Measurement.date <= end_dt).all()
    agg_list = list(np.ravel(agg_query))
    return jsonify(agg_list)

if __name__ == "__main__":
    app.run(debug=True)