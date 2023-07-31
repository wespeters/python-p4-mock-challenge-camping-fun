#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)  

class Home(Resource):
    def get(self):
        return ''

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        return make_response(jsonify([camper.to_dict(only=('id', 'name', 'age')) for camper in campers]), 200)

    def post(self):
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')

        try:
            new_camper = Camper(name=name, age=age)
            db.session.add(new_camper)
            db.session.commit()
        except:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        return make_response(jsonify(new_camper.to_dict(only=('id', 'name', 'age'))), 201)

class CamperDetail(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper is None:
            return make_response(jsonify({"error": "Camper not found"}), 404)
        return make_response(jsonify(camper.to_dict()), 200)

    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper is None:
            return make_response(jsonify({"error": "Camper not found"}), 404)

        data = request.get_json()
        name = data.get('name')
        age = data.get('age')

        try:
            if name is not None:
                camper.name = name
            if age is not None:
                camper.age = age
            db.session.commit()
        except:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        return make_response(jsonify(camper.to_dict(only=('id', 'name', 'age'))), 202)

class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        return make_response(jsonify([activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities]), 200)

class ActivityDetail(Resource):
    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if activity is None:
            return make_response(jsonify({"error": "Activity not found"}), 404)

        db.session.delete(activity)
        db.session.commit()

        return make_response('', 204)

class Signups(Resource):
    def post(self):
        data = request.get_json()
        camper_id = data.get('camper_id')
        activity_id = data.get('activity_id')
        time = data.get('time')

        try:
            new_signup = Signup(camper_id=camper_id, activity_id=activity_id, time=time)
            db.session.add(new_signup)
            db.session.commit()
        except:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        return make_response(jsonify(new_signup.to_dict()), 201)


api.add_resource(Home, '/')
api.add_resource(Campers, '/campers')
api.add_resource(CamperDetail, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityDetail, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
