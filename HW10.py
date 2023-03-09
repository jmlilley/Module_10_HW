#################################################
# Imports
#################################################
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Create Engine
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data from the last 12 months of data as json"""
    precip_results = []

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    year_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    sel = [Measurement.date, 
           Measurement.prcp]
    year_prcp = session.query(*sel).\
        filter(Measurement.date >= year_ago).\
        group_by(Measurement.date).all()

    for date, prcp_value in year_prcp:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp_value
        precip_results.append(precipitation_dict)

    return jsonify(precip_results)

@app.route("/api/v1.0/stations")
def stations():
    """Return the list of station ids and their names as json"""
    station_results = []
    
    stations = session.query(Station.station, Station.name).all()
    
    for id, name in stations:
        station_dict = {}
        station_dict["Station ID"] = id
        station_dict["Station Name"] = name
        station_results.append(station_dict)

    return jsonify(station_results)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature data of the most active station as json"""
    temp_results = []

    sel = [Measurement.station,
       func.count(Measurement.station)]
    most_active = session.query(*sel).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    
    most_active_station = most_active[0][0]

    sel = [Measurement.date, 
           Measurement.tobs]
    ma_temps = session.query(*sel).\
        filter(Measurement.station == most_active_station).all()
    
    for date, temp in ma_temps:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = temp
        temp_results.append(temp_dict)

    return jsonify(temp_results)

@app.route("/api/v1.0/<start>")
def start_stats(start):
    """Return the summary data for all temperatures on of after the date as json"""
    summary_stats_starts = []
    
    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    start_averages = session.query(*sel).\
        filter(Measurement.date >= start).all()
    
    for min, max, avg in ma_temps:
        stats_dict = {}
        stats_dict["Min Temperature"] = min
        stats_dict["Max Temperature"] = max
        stats_dict["Average Temperature"] = avg
        summary_stats_starts.append(stats_dict)

    return jsonify(summary_stats_starts)

@app.route("/api/v1.0/<start>/<end>")
def start_stop(start, end):
    """Return the summary data for all temperatures between the dates as json"""
    summary_stats_between = []
    
    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    between_averages = session.query(*sel).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    for min, max, avg in between_averages:
        between_dict = {}
        between_dict["Min Temperature"] = min
        between_dict["Max Temperature"] = max
        between_dict["Average Temperature"] = avg
        summary_stats_between.append(between_dict)

    return jsonify(summary_stats_between)


@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"Precipitation data for the most recent 12 months of data:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"A list of stations in the database:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Temperature data for the most active station:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Temperature statistics for all temperatures on or after the start date:<br/>"
        f"/api/v1.0/start_date<start><br/><br/>"
        f"Temperature statistics for all temperatures between the start and stop dates:<br/>"
        f"/api/v1.0/start_date<start>/end_date<end>"
    )


if __name__ == "__main__":
    app.run(debug=True)
