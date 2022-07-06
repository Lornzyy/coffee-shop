import os
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# CORS Headers


@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS"
    )
    return response


db_drop_and_create_all()


# ROUTES


@app.route('/drinks')
def get_drinks():

    drinks_present = Drink.query.all()

    if len(drinks_present) <= 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.short()for drink in drinks_present]
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):

    try:
        drinks_details = Drink.query.all()


        return jsonify({
            'success': True,
            'drinks': [drink.long()for drink in drinks_details]
        }), 200

    except Exception:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):

    try:
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        if new_title is None or new_recipe is None:
            abort(422)

    

        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink_details(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        body = request.get_json()
        modified_title = body.get('title')
        modified_recipe = body.get('recipe')
    
    
        if modified_title:
            Drink.title = modified_title

        if modified_recipe:
            for details in modified_recipe:
                color = details.get('color')
                name = details.get('name')
                parts = details.get('parts')

            drink.recipe = json.dumps(modified_recipe)

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except Exception:
        abort(400)


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'deleted': drink_id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401


@app.errorhandler(AuthError)
def invalid_authentication(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error,
    }), error.status_code
