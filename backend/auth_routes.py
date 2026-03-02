from flask import Flask, request, jsonify
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

users = {}

@app.route('/')
def home():
    return "Backend running"

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    if username in users:
        return jsonify({"message": "User already exists"}), 400

    users[username] = generate_password_hash(password)

    return jsonify({"message": "Signup successful"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username not in users:
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(users[username], password):
        return jsonify({"message": "Invalid password"}), 401

    token = jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token}), 200


if __name__ == "__main__":
    app.run(debug=True)
