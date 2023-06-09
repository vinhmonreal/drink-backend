from app.blueprints.social.routes import drinks
from . import bp
from app.blueprints.api.helpers import token_required
from app.models import AddDrinks, User, MarvelCharacter
from flask import jsonify, request, url_for, abort
from flask_cors import cross_origin

@bp.get('/characters')
# @token_required
def characters():
    characters = MarvelCharacter.query.all()
    return jsonify([character.to_dict() for character in characters])        

@bp.get('/user/<username>')
# @token_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'user not found'}), 404
    return jsonify(user.to_dict())

@bp.route('/user/addcharacter', methods=['POST', 'GET'])
# @token_required
def addcharacter():
    content = request.get_json()
    username= content['username']
    password= content['password']
    name = content['name']
    description = content['description']
    comics_appeared_in = content['comics_appeared_in']
    super_power = content['super_power']
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        owner_id = user.token
        character = MarvelCharacter(name=name, description=description, comics_appeared_in=comics_appeared_in, super_power=super_power, owner_id=owner_id)
        character.commit()
        return jsonify(character.to_dict()), 201
    else:
        return jsonify({'error': 'user not found or invalid password'}), 404
    
    
@bp.route('/verifyuser', methods=['POST', 'GET'])
def verifyUser():
    
    content = request.get_json()
    username= content['username']
    password= content['password']
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify(user.to_dict())
    else:
        return jsonify({'error': 'user not found or invalid password'}), 404
    # comtents = request.get_json()
    
    
@bp.route('/user/favdrinks', methods=[ 'GET', 'POST'])
def getuserDrinks():
    
    content = request.get_json()
    token = content['token']
    user = User.query.filter_by(token=token).first()
    if user:
        userdrinks = AddDrinks.query.filter_by(owner_id=user.token).all()
        return jsonify([drink.to_dict() for drink in userdrinks])
    else:
        return jsonify({'error': 'user not found'}), 404
    

@bp.route('/user/adddrink/<username>', methods=['POST', 'GET'])
# @token_required
def addfavdrinks(username):
    
    content = request.get_json()
    token = content['token']
    idDrink = content['idDrink']
    strDrink = content['strDrink']
    strDrinkThumb = content['strDrinkThumb']
    
    user = User.query.filter_by(username=username).first()
    if user:
        if user.token == token:
            drink = AddDrinks(idDrink=idDrink, strDrink=strDrink, strDrinkThumb=strDrinkThumb, owner_id=token)
            drink.commit()
            return jsonify(drink.to_dict()), 201
        else:
            return jsonify({'error': 'user not found'}), 404
    else:
        return jsonify({'error': 'user not found'}), 404
    
    
@bp.route('/user/removedrink/<username>', methods=['POST', 'GET'])
# @token_required
def deletefavdrinks(username):
    
    content = request.get_json()
    token = content['token']
    idDrink = content['idDrink']
    user = User.query.filter_by(username=username).first()
    
    if user:
        if user.token == token:
            drink = AddDrinks.query.filter_by(idDrink=idDrink, owner_id=token).first()
            if drink:
                drink.delete()
                return jsonify({'message': 'drink deleted'}), 201
            else:
                return jsonify({'error': 'drink not found'}), 404
        else:
            return jsonify({'error': 'user not found'}), 404
    else:
        return jsonify({'error': 'user not found'}), 404
    
 

@bp.route('/auth/register', methods=['POST', 'GET'])
def register():
    
    content = request.get_json()
    username= content['username']
    password= content['password']
    email = content['email']
    
    try:
        int(username)
        return jsonify({'error': 'username must be a string'}), 408
    except:
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'username already exists'}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'email already exists'}), 409
        user = User(username=username, email=email)
        user.hash_password(password)
        user.add_token()
        user.commit()
        return jsonify(user.to_dict()), 201
    
    # ###########################
@bp.route('/user/addcomment/<username>', methods=['POST', 'GET'])
def addcomment(username):
    
    content = request.get_json()
    
    token = content['token']
    comment = content['comment']
    id = content['id']  
    
    user = User.query.filter_by(username=username).first()
    if user:
        if user.token == token:
            drink = AddDrinks.query.filter_by(id=id, owner_id=token).first()
            if drink:
                drink.strDrinkThumb = comment
                drink.commit()
                return jsonify(drink.to_dict()), 201
            else:
                return jsonify({'error': 'drink not found'}), 404            
        else:
            return jsonify({'error': 'user not found'}), 404
    else:        
        return jsonify({'error': 'user not found'}), 404
    
@bp.route('/user/deletecomment/<username>', methods=['POST', 'GET'])
def deletecomment(username):
    
    content = request.get_json()
    
    token = content['token']
    id = content['id']  
    
    user = User.query.filter_by(username=username).first()
    if user:
        if user.token == token:
            drink = AddDrinks.query.filter_by(id=id, owner_id=token).first()
            if drink:
                drink.strDrinkThumb = ''
                drink.commit()
                return jsonify(drink.to_dict()), 201
            else:
                return jsonify({'error': 'drink not found'}), 404            
        else:
            return jsonify({'error': 'user not found'}), 404
    else:        
        return jsonify({'error': 'user not found'}), 404