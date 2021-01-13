#!/usr/bin/env python
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from datetime import datetime
from flask_jsonpify import jsonify
from flask_cors import CORS, cross_origin

db_connect = create_engine('sqlite:///car.db', connect_args={'check_same_thread': False});
app = Flask(__name__);
api = Api(app);
CORS(app);

class Cars(Resource):
	def get(self):
		conn = db_connect.connect()
		query = conn.execute("select id, name, brand, color, immatriculation, controle_technique from car")
		cars = [dict(zip(tuple(query.keys()) ,i)) for i in query.cursor]
		for car in cars:
			for key, value in car.items():
				if key == 'controle_technique':
					car[key] = datetime.fromtimestamp(value).strftime("%d/%m/%Y")
		result = {'cars': cars}
		return jsonify(result)

class Car(Resource):
	def get(self, car_id):
		conn = db_connect.connect()
		query = conn.execute("select id, name, color, immatriculation, controle_technique from car where id=%d " %int(car_id))
		cars = [dict(zip(tuple(query.keys()) ,i)) for i in query.cursor]
		for car in cars:
			for key, value in car.items():
				if key == 'controle_technique':
					car[key] = datetime.fromtimestamp(value).strftime("%d/%m/%Y")
		return jsonify(cars[0])

class Reparations(Resource):
	def get(self, car_id):
		conn = db_connect.connect()
		query = conn.execute("select id, type, kilometrage, description, adresse_garage, cout, date from reparation WHERE car_id=%d " %int(car_id))
		reparations =[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
		for reparation in reparations:
			for key, value in reparation.items():
				if key == 'date':
					reparation[key] = datetime.fromtimestamp(value).strftime("%d/%m/%Y")
		result = {'reparations': reparations}
		return jsonify(result)


api.add_resource(Cars, '/cars')
api.add_resource(Car, '/car/<car_id>')
api.add_resource(Reparations, '/reparations/<car_id>')

if __name__ == '__main__':
	app.run(port='5002')
