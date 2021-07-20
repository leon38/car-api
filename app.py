#!/usr/bin/env python
from flask import Flask, request, Response
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
api = Api(app)
CORS(app)
db = SQLAlchemy(app)


class Cars(Resource):
    @app.route("/cars", methods=["GET"])
    def get_cars():
        cars = Car.query.all()
        return jsonify([i.serialize for i in cars])

    @app.route("/cars/<int:car_id>", methods=["GET"])
    def get_car(car_id):
        car = Car.query.get(car_id)
        if car is None:
            return Response({}, status=404, mimetype='application/json')
        return jsonify(car.serialize)

    @app.route("/cars", methods=["POST"])
    def add_car():
        data = request.get_json(force=True)
        car = Car(data['name'],
                  data['brand'],
                  data['color'],
                  data['license_plate'],
                  datetime.datetime.strptime(data['technical_inspection'], "%d/%m/%Y"),
                  data['tire_dimensions'])
        db.session.add(car)
        db.session.commit()
        return jsonify(car.serialize)

    @app.route("/cars/<int:car_id>", methods=["PUT"])
    def update_car(car_id):
        data = request.get_json(force=True)
        car = Car.query.get(car_id)
        car.name = data['name']
        car.brand = data['brand']
        car.color = data['color']
        car.license_plate = data['license_plate']
        car.technical_inspection = datetime.datetime.strptime(data['technical_inspection'], "%d/%m/%Y")
        car.tire_dimensions = data['tire_dimensions']
        db.session.commit()
        return jsonify(car.serialize)


class Repairments(Resource):
    @app.route("/repairments", methods=["GET"])
    def get_repairments():
        repairments = Repairment.query.all()
        return jsonify([i.serialize for i in repairments])

    @app.route("/repairments", methods=["POST"])
    def add_repairment():
        data = request.get_json(force=True)
        repairment = Repairment(
                  data['type'],
                  data['kilometers'],
                  data['description'],
                  data['garage_address'],
                  data['price'],
                  datetime.datetime.strptime(data['date'], "%d/%m/%Y"),
                  data['car_id'])
        db.session.add(repairment)
        db.session.commit()
        return jsonify(repairment.serialize)

    @app.route("/repairments/<int:repairment_id>", methods=["PUT"])
    def update_repairment(repairment_id):
        data = request.get_json(force=True)
        repairment = Repairment.query.get(repairment_id)
        repairment.type = data['type']
        repairment.kilometers = data['kilometers']
        repairment.description = data['description']
        repairment.garage_address = data['garage_address']
        repairment.price = data['price']
        repairment.date = datetime.datetime.strptime(data['date'], "%d/%m/%Y")
        db.session.commit()
        return jsonify(repairment.serialize)

    @app.route("/repairments/<repairment_id>", methods=["DELETE"])
    def delete_repairment(repairment_id):
        repairment = Repairment.query.get(repairment_id)
        db.session.delete(repairment)
        db.session.commit()
        return Response({}, status=204, mimetype='application/json')

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    brand = db.Column(db.String(30), unique=False, nullable=False)
    color = db.Column(db.String(30), unique=False, nullable=False)
    license_plate = db.Column(db.String(9), unique=True, nullable=False)
    technical_inspection = db.Column(db.DateTime, unique=False, nullable=False)
    tire_dimensions = db.Column(db.String(50), unique=False, nullable=True)
    repairments = db.relationship('Repairment', backref='car', lazy=True)

    def __init__(self, name, brand, color, license_plate, technical_inspection, tire_dimensions):
        self.name = name
        self.brand = brand
        self.color = color
        self.license_plate = license_plate
        self.technical_inspection = technical_inspection
        self.tire_dimensions = tire_dimensions

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'color': self.color,
            'license_plate': self.license_plate,
            'technical_inspection': self.technical_inspection.strftime("%d/%m/%Y"),
            'tire_dimensions': self.tire_dimensions,
            'repairments': [repairment.serialize for repairment in self.repairments]
        }



class Repairment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), unique=True, nullable=False)
    kilometers = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String(255), unique=True, nullable=False)
    garage_address = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Float, unique=True, nullable=False)
    date = db.Column(db.DateTime, unique=False, nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)

    def __init__(self, type, kilometers, description, garage_address, price, date, car_id):
        self.type = type
        self.kilometers = kilometers
        self.description = description
        self.garage_address = garage_address
        self.price = price
        self.date = date
        self.car_id = car_id


    @property
    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'kilometers': self.kilometers,
            'description': self.description,
            'garage_address': self.garage_address,
            'price': self.price,
            'car_id': self.car_id,
            'date': self.date.strftime("%d/%m/%Y")
        }


if __name__ == '__main__':
    app.run()
