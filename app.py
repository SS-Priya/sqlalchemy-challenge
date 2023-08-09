import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func , extract
import datetime as dt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *

from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///hawaii.sqlite") 

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine,reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station=Base.classes.station

# Flask Setup

app = Flask(__name__)

# Start at the homepage.
# List all the available routes.

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Returns json with the date as the key and the value as the precipitation 
# Only returns the jsonified precipitation data for the last year in the database

@app.route("/api/v1.0/precipitation")

def precipitation():
   
    session = Session(engine)

    # Query to find the last year in the measurement table

    last_year = session.query(extract('year', Measurement.date)).\
                  order_by(Measurement.date.desc()).first()
    
    # Query to return last year dates and precipitation from measurement table

    results = session.query(Measurement.date,Measurement.prcp).\
                            filter(extract('year', Measurement.date) == last_year[0]).all()

    session.close()

    # storing results to a dictionary

    all_prcp= []
    for date,prcp in results:
        prcp_dict = {date:prcp}
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

# Returns jsonified data of all of the stations in the database

@app.route("/api/v1.0/stations")

def stations():
   
    session = Session(engine)

    # Query to return list of stations

    results = session.query(Station.station).all()
             
    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Query the dates and temperature observations of 
# the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")

def tobs():

    session = Session(engine)

    # Query to list the stations and their counts in desc order to find most active station 

    active_stations = session.query(Measurement.station,\
                             (func.count(Measurement.station)).label('total')).\
                             filter(Measurement.station == Station.station).\
                             group_by(Measurement.station).order_by(desc('total'))
    
    # Assigning most active station value to a variable 

    most_active = active_stations[0][0]

    # Query to find Last year in the most active station

    last_year = session.query(extract('year', Measurement.date)).\
                  filter(Measurement.station==most_active).\
                  order_by(Measurement.date.desc()).first()
    
    # Query to find date and temperature for the last year in most active station
     
    temp_result = session.query(Measurement.date,Measurement.tobs).\
                          filter(Measurement.station==most_active).\
                          filter(extract('year', Measurement.date) == last_year[0]).all()

    session.close()

    all_temp= []
    for date,temp in temp_result:
        temp_dict = {date:temp}
        all_temp.append(temp_dict)

    return jsonify(all_temp)

# For a specified start date, calculate TMIN, TAVG, and TMAX \
# for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")

def start_date(start):
  
    session = Session(engine)

    # Finding last date in the dataset

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = recent_date[0]

    results = session.query(func.min(Measurement.tobs),\
                          func.avg(Measurement.tobs),\
                          func.max(Measurement.tobs)).\
                          filter(Measurement.date >= start).\
                          filter(Measurement.date <= last_date).all()
   
    session.close()

    analysis = list(np.ravel(results))
    return jsonify(analysis)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX
# for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start,end):
   
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs),\
                          func.avg(Measurement.tobs),\
                          func.max(Measurement.tobs)).\
                          filter(Measurement.date >= start).\
                          filter(Measurement.date <= end).all()
   
    session.close()

    analysis = list(np.ravel(results))
    return jsonify(analysis)


if __name__ == '__main__':
    app.run()
