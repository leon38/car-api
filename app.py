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
	@app.route("/only-cars", methods=["GET"])
	def getCars():
		conn = db_connect.connect()
		query = conn.execute("SELECT id, name, brand, color, immatriculation, controle_technique FROM car")
		cars = [dict(zip(tuple(query.keys()) ,i)) for i in query.cursor]
		for car in cars:
			for key, value in car.items():
				if key == 'controle_technique':
					car[key] = datetime.fromtimestamp(value).strftime("%d/%m/%Y")
		result = {'cars': cars}
		return jsonify(result)

class CarsWithReparations(Resource):
	@app.route("/cars", methods=["GET"])
	def getCarsAndReparations():
		conn = db_connect.connect()
		query = conn.execute("SELECT id, name, brand, color, immatriculation, controle_technique FROM car")
		cars = [dict(zip(tuple(query.keys()) ,i)) for i in query.cursor]
		for car in cars:
			query = conn.execute("SELECT id, type, kilometrage, description, adresse_garage, cout, date FROM reparation WHERE car_id=%d ORDER BY date" %int(car['id']))
			reparations =[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
			car['reparations'] = reparations		
		result = {'cars': cars}
		return jsonify(result)
		
class Car(Resource):
	@app.route("/car", methods=["GET"])
	def getCar(car_id):
		conn = db_connect.connect()
		query = conn.execute("select id, name, color, immatriculation, controle_technique from car where id=%d " %int(car_id))
		cars = [dict(zip(tuple(query.keys()) ,i)) for i in query.cursor]
		for car in cars:
			for key, value in car.items():
				if key == 'controle_technique':
					car[key] = datetime.fromtimestamp(value).strftime("%d/%m/%Y")
		return jsonify(cars[0])

class ReparationsByCar(Resource):
	@app.route("/reparations/<car_id>", methods=["GET"], endpoint="get")
	def getReparationsByCar(car_id):
		conn = db_connect.connect()
		query = conn.execute("select id, type, kilometrage, description, adresse_garage, cout, date from reparation WHERE car_id=%d ORDER BY date" %int(car_id))
		reparations =[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
		for reparation in reparations:
			for key, value in reparation.items():
				if key == 'date':
					reparation[key] = datetime.fromtimestamp(value).strftime("%d/%m/%Y")
		result = {'reparations': reparations}
		return jsonify(result)

class PostReparation(Resource): 
	@app.route("/reparation", methods=["POST"], endpoint="post")	
	def addReparation():
		request_data = request.json
		conn = db_connect.connect()
		date = str(request_data['date']).split('/')
		timestamp = datetime.fromisoformat(date[2] + "-" + date[1] + "-" + date[0]).timestamp()
		query = conn.execute('INSERT INTO reparation (car_id, type, kilometrage, description, adresse_garage, cout, date) VALUES ({}, "{}", {}, "{}", "{}", {}, {})'.format(int(request_data['car_id']), str(request_data['type']), int(request_data['kilometrage']), str(request_data['description']).replace("'","\'"), str(request_data['adresse_garage']).replace("'","\'"), float(request_data['cout']), int(timestamp)))
		result = {}
		return jsonify(result)

class Reparations(Resource):
	@app.route("/reparations", methods=["GET"])
	def getAllReparations(self):
		conn = db_connect.connect()
		query = conn.execute("select id, type, kilometrage, description, adresse_garage, cout, date from reparation ORDER BY date")
		reparations =[dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
		for reparation in reparations:
			for key, value in reparation.items():
				if key == 'date':
					reparation[key] = datetime.fromtimestamp(value).strftime("%d/%m/%Y")
		result = {'reparations': reparations}
		return jsonify(result)
	

if __name__ == '__main__':
	app.run(port='5002')
