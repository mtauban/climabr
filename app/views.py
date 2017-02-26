from datetime import datetime, timedelta

from app import app, db
from flask import render_template, jsonify, abort, request
from .forms import LoginForm
from .models import Config, Sensor, Measurement, Category, Location, pLast


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/')
@app.route('/index')
def index():
    u = Config.query.all()
    m = Measurement.query.order_by('-id').first()
    return render_template('index.html', configs=u, measure=m)


@app.route('/measure/<sensor_id>/<type>', methods=['get'])
@app.route('/measure/<sensor_id>/', methods=['get'])
def get_measure(sensor_id, type='D'):
    delays = {'H' : 1, 'D': 24, 'W': 170, 'M': 5040, 'Y': 61000}
    sensor = Sensor.query.get(sensor_id)
    if sensor is None:
        abort(404)
    ms = Measurement.query.join(Sensor).filter(Sensor.id == sensor.id,
                                               Measurement.date > datetime.now() - timedelta(hours=delays[type]))
    return render_template('measure.html', sensor=sensor, measures=ms)


# API DEFINITION

# MEASURES
# Api is open to all kind of measurements
# If receives an unknown sensor, it will add the given sensor !
# Integrates the measurement in the database
# retrieves data
@app.route('/api/v1/measure/<sensor_id>/', methods=['POST'])
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
    return jsonify({'config': i.toJSON() for i in u})


@app.route('/api/v1/config', methods=['POST'])  # Create a configuration, or update
def create_config():
    if not request.json or not 'key' in request.json or not 'value' in request.json:
        abort(400)
    data = request.get_json()
    q = Config(data.get('key'), data.get('value'))
    db.session.merge(q)
    db.session.commit()
    u = [q]
    return jsonify({'config': i.toJSON() for i in u})


@app.route('/api/v1/config/<key>', methods=['PUT'])  # Update a configuration
def update_config(key):
    q = Config.query.get(key)
    if q is None:
        abort(404)
    q.value = request.json.get('value', q.value)
    db.session.commit()
    u = [q]
    return jsonify({'config': i.toJSON() for i in u})
