App.py



from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

app= Flask(__name__)

app.config['SECRET_KEY'] = 'Bj7qxGUEPQvTUpee9DqFltEqlPvEIod1yK6Pr89qFxJJtFfZKNXnhuARVgYIfoCM8ax0Db4D2LIZtxxbkrM1HZkmGZh5OUC3j6HtxgVIZiud3fifcOSa/xJZ5VNePG2VA/mWELM5XTtLi5C8Yfv3ex2QN5Hu0E8k7lY9sTHo1N4='
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt=JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



@app.route('/api/signup',methods=['POST'])
def signup():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({"msg":"Username or email already exists"}),409

    user=User(username=data['username'],email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return jsonify({"msg": "User created successfully", "access_token": access_token}), 201

@app.route('/api/login',methods=['POST'])
def login():
    data = request.get_json()
    #find by username
    user=User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "Invalid username or password"}), 401
    access_token = create_access_token(identity=user.id)

    return jsonify({"msg": "User login successfully", "access_token": access_token}), 200


@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    return jsonify({
        "username": user.username,
        "email": user.email
    }), 200


# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
