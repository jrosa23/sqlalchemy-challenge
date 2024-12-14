# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta

# Initialize Flask app
app = Flask(__name__)

#################################################
# Database Setup
#################################################
# reflect an existing database into a new model
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables and the References to the tables
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Routes
#################################################
# Route 1: Homepage
@app.route("/")
def home():
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>"
    )

# Route 2: Precipitation data for the last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent = session.query(func.max(measurement.date)).scalar()
    most_recent_date = pd.to_datetime(most_recent)
    prior = most_recent_date - relativedelta(months=12)
    prior_twelve = prior.strftime('%Y-%m-%d')
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prior_twelve).all()
    session.close()

    precip_data = {date: prcp for date, prcp in results}
    return jsonify(precip_data)

# Route 3: List of stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    station_list = [station[0] for station in results]
    return jsonify(station_list)

# Route 4: Temperature observations of the most active station for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent = session.query(func.max(measurement.date)).scalar()
    most_recent_date = pd.to_datetime(most_recent)
    prior = most_recent_date - relativedelta(months=12)
    prior_twelve = prior.strftime('%Y-%m-%d')

    # Find the most active station
    most_active_station = (
        session.query(measurement.station)
        .group_by(measurement.station)
        .order_by(func.count(measurement.station).desc())
        .first()[0]
    )

    results = (
        session.query(measurement.date, measurement.tobs)
        .filter(measurement.station == most_active_station)
        .filter(measurement.date >= prior_twelve)
        .all()
    )
    session.close()

    tobs_data = [{date: tobs} for date, tobs in results]
    return jsonify(tobs_data)

# Route 5: Temperature stats from a start date
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    session = Session(engine)
    results = (
        session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))
        .filter(measurement.date >= start)
        .all()
    )
    session.close()

    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temp_stats)

# Route 6: Temperature stats for a start-end date range
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_range(start, end):
    session = Session(engine)
    results = (
        session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))
        .filter(measurement.date >= start)
        .filter(measurement.date <= end)
        .all()
    )
    session.close()

    temp_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temp_stats)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
