#!flask/bin/python
from os import getenv
from app import app

app.run(host=getenv('IP', '0.0.0.0'),port=int(getenv('PORT', '8080')),debug=True)
