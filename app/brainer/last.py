from datetime import datetime, timedelta

from app import app, db, models


def printLast():
    ctx = app.test_request_context()
    ctx.push()
    last = models.Measurement.query\
        .join(models.Sensor)\
        .filter(models.Measurement.date > datetime.now() - timedelta(hours=1))\
        .order_by(models.Measurement.date.desc()).all()
    ctx.pop()
    return last
