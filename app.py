from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Database config (use DATABASE_URL from Render later)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Roles with percentages
ROLE_PERCENTAGES = {
    "TRAINEE": 0.20,
    "JUNIOR MECH": 0.30,
    "MECHANIC": 0.40,
    "SENIOR MECH": 0.50
}

# User (for login)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Members
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

# Daily earnings
class Earning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)

@app.route("/init-admin", methods=["POST"])
def init_admin():
    """Create admin user (run once)"""
    if Admin.query.filter_by(username="sks_mechanics").first():
        return jsonify({"message": "Admin already exists"}), 400
    hashed = generate_password_hash("sks@1188", method="sha256")
    admin = Admin(username="sks_mechanics", password=hashed)
    db.session.add(admin)
    db.session.commit()
    return jsonify({"message": "Admin created"})

@app.route("/add-member", methods=["POST"])
def add_member():
    data = request.json
    member = Member(name=data["name"], role=data["role"])
    db.session.add(member)
    db.session.commit()
    return jsonify({"message": "Member added"})

@app.route("/add-earning", methods=["POST"])
def add_earning():
    data = request.json
    earning = Earning(member_id=data["member_id"], amount=data["amount"])
    db.session.add(earning)
    db.session.commit()
    return jsonify({"message": "Earning added"})

@app.route("/calculate-salary/<int:member_id>", methods=["GET"])
def calculate_salary(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    total = db.session.query(db.func.sum(Earning.amount)).filter_by(member_id=member_id).scalar() or 0
    percentage = ROLE_PERCENTAGES.get(member.role.upper(), 0)
    salary = total * percentage
    return jsonify({
        "member": member.name,
        "role": member.role,
        "total_earned": total,
        "salary": salary
    })

if __name__ == "__main__":
    app.run(debug=True)
