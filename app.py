from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config["JWT_SECRET_KEY"] = "secretkey123"
jwt = JWTManager(app)

# Database connection
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create table if it doesn't exist
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")
conn.commit()
conn.close()


# Home route
@app.route("/")
def home():
    return "Backend Running Successfully"


# Register user
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    conn = get_db()
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (data["username"], data["password"], data["role"])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully"})


# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data["username"], data["password"])
    ).fetchone()
    conn.close()

    if user:
        token = create_access_token(
            identity=user["username"],   # identity must be string
            additional_claims={"role": user["role"]}   # store role here
        )

        return jsonify(access_token=token)

    return jsonify({"message": "Invalid credentials"}), 401


# Admin route (role protected)
@app.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    claims = get_jwt()

    if claims["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    return jsonify({"message": "Welcome Admin"})


# Normal user route
@app.route("/user", methods=["GET"])
@jwt_required()
def user():
    username = get_jwt_identity()
    return jsonify({"message": f"Welcome {username}"})


# Run server
if __name__ == "__main__":
    app.run(debug=True)