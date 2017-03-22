from datetime import datetime, timedelta

from app import app, db
from flask import render_template, jsonify, abort, request
from .models import Config, Sensor, Measurement, Category, Location, pLast




@app.route('/')
@app.route('/index')
def index():
    u = Config.query.all()
    m = Measurement.query.order_by('-id').first()
    return render_template('index.html', configs=u, measure=m)


@app.route('/sensor')
def sensor_list():
    sensors = Sensor.query.all()
    return render_template('sensor.html', sensors=sensors)




@app.route('/measure/<sensor_id>/<type>', methods=['get'])
@app.route('/measure/<sensor_id>/', methods=['get'])
def get_measure(sensor_id, type='H'):
    delays = {'H' : 1, 'D': 24, 'W': 170, 'M': 5040, 'Y': 61000}
    sensor = Sensor.query.get(sensor_id)
    if sensor is None:
        abort(404)
    ms = Measurement.query.join(Sensor).filter(Sensor.id == sensor.id,
                                               Measurement.date > datetime.now() - timedelta(hours=delays[type])).order_by(Measurement.date.desc())
    return render_template('measure.html', sensor=sensor, measures=ms)


# API DEFINITION

# MEASURES
# Api is open to all kind of measurements
# If receives an unknown sensor, it will add the given sensor !
# Integrates the measurement in the database
# retrieves data
@app.route('/api/v1/measure/<sensor_id>', methods=['POST'])
def add_measure(sensor_id):
    sensor = Sensor.query.get(sensor_id)
    if sensor is None:  # Sensor is not known
        # Look for default category
        cat = Category.query.get(0)
        if cat is None:
            cat = Category('Default', 'Default')
            db.session.add(cat)
            db.session.commit()

        loc = Location.query.get(0)
        if loc is None:
            loc = Location('Default', 'Default')
            db.session.add(loc)
            db.session.commit()

        sensor = Sensor(sensor_id, 'Not Defined', cat, loc)
        db.session.add(sensor)
    if not request.json or not 'value' in request.json:
        abort(400)
    data = request.get_json()

    measuredvalue = float(data.get('value')) # @TODO: Check if value is float ...
    # retrieve last two measurement to check if value is changeing
    lastm = Measurement.query.join(Sensor).filter(Sensor.id == sensor.id). \
        order_by(Measurement.date.desc()).limit(2).all()
    tol = 0.005 # @TODO: Make it a config variable at some point
    if len(lastm) == 2 and ( abs(float(lastm[0].value) - float(lastm[1].value)) <= tol) and ( abs(float(lastm[0].value)  - measuredvalue) <= tol) : # we have two items already in the list, we have to check if last two are equals, if so, we update last one with new timestamp
            lastm[0].date = datetime.now()
            m = lastm[0]
    else:     # creates a measurement value
        m = Measurement(sensor, data.get('value'), datetime.now())
        db.session.add(m)

    db.session.commit()
    return jsonify(m.toJSON())


# CONFIG
@app.route('/api/v1/config', methods=['GET'])  # Get all keys
@app.route('/api/v1/config/<key>', methods=['GET'])  # Get only specified
def get_config(key=None):
    """ try to load the value """
    if not key:  # query all if no value provided, happens when first route is called
        u = Config.query.all()
    else:  # query given key otherwise
        q = Config.query.get(key)
        if q is None:  # fails if key not found
            abort(404)
        else:  # prepare for output otherwise
            u = [q]
    return jsonify( config = [ i.toJSON() for i in u ])


@app.route('/api/v1/config', methods=['POST'])  # Create a configuration, or update
def create_config():
    if not request.json or not 'key' in request.json or not 'value' in request.json:
        abort(400)
    data = request.get_json()
    q = Config(data.get('key'), data.get('value'))
    db.session.merge(q)
    db.session.commit()
    u = [q]
    return jsonify( config = [ i.toJSON() for i in u ])


@app.route('/api/v1/config/<key>', methods=['PUT'])  # Update a configuration
def update_config(key):
    q = Config.query.get(key)
    if q is None:
        abort(404)
    q.value = request.json.get('value', q.value)
    db.session.commit()
    u = [q]
    return jsonify( config = [ i.toJSON() for i in u ])
