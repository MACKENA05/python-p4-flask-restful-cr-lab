#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get(self):
        plants = Plant.query.all()
        return jsonify([plant.to_dict() for plant in plants])
    
    def post(self):
    
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        data = request.get_json()

        required_fields = ['name', 'image', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=float(data['price']),  
            )

            db.session.add(new_plant)
            db.session.commit()

            response = make_response(new_plant.to_dict(), 200)

            return response
        
        except ValueError as e:
            db.session.rollback()
            return jsonify({"error": "Invalid price value"}), 400
        except KeyError as e:
            db.session.rollback()
            return jsonify({"error": f"Missing field: {str(e)}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        

api.add_resource(Plants, '/plants')

class PlantByID(Resource):
    def get(self,id):
        plant = Plant.query.filter_by(id = id).first()
        response = make_response(plant.to_dict(),200)
        return response
    
api.add_resource(PlantByID, '/plants/<int:id>')


class PlantByID(Resource):
    pass
        

if __name__ == '__main__':
    app.run(port=5555, debug=True)
