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


@app.route('/')
def home():
    return ''


@app.route('/campers', methods=['GET', 'POST'])
def campers():
    if request.method == 'GET':
        camper_list = [camper.to_dict(rules=('-signups',)) for camper in Camper.query.all()]

        return make_response(camper_list, 200)
    
    if request.method == 'POST':
        data = request.json
        try:
            camper = Camper(name = data['name'], age = data['age'])
            db.session.add(camper)
            db.session.commit()

            return make_response(camper.to_dict(rules=('-signups',)), 201)
        
        except:
            return make_response({'errors': ['validation errors']}, 400)
        

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if request.method == 'GET':
        if camper == None:
            return make_response({'error': 'Camper not found'}, 404)
        
        return make_response(camper.to_dict(), 200)

    if request.method == 'PATCH':
        if camper == None:
            return make_response({'error': 'Camper not found'}, 404)
        
        data = request.json
        try:
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.commit()

            return make_response(camper.to_dict(), 202)
        
        except:
            return make_response({"errors": ["validation errors"]}, 400)
        

@app.route('/activities', methods=['GET'])
def activties():
    if request.method == 'GET':
        activity_list = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]

        return make_response(activity_list, 200)
    

@app.route('/activities/<int:id>', methods=['GET', 'DELETE'])
def activty_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if request.method == 'GET':
        if activity == None:
          return make_response({'error': 'Activity not found'}, 404)
        
        return make_response(activity.to_dict(), 200)  
    
    if request.method == 'DELETE':
        if activity == None:
            return make_response({'error': 'Activity not found'}, 404)

        Signup.query.filter(Signup.activity_id == activity.id).delete()
        db.session.delete(activity)
        db.session.commit()
        return make_response('', 204)
    

@app.route('/signups', methods=['GET', 'POST'])
def signups():
    if request.method == 'GET':
        signup_list = [signup.to_dict() for signup in Signup.query.all()]

        return make_response(signup_list, 200)
    
    if request.method == 'POST':
        data = request.json
        try:
            signup = Signup(camper_id = data['camper_id'], activty_id = data['activity_id'], time = data['time'])
            db.session.add(signup)
            db.session.commit()

            return make_response(signup.to_dict(), 201)
        
        except:
            return make_response({'errors': ['validation errors']}, 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
