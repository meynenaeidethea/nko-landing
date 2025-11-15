from flask import Blueprint, jsonify
from backend.models import db, Organization

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/pending", methods=["GET"])
def pending():
    orgs = Organization.query.filter_by(approved=False).all()

    return jsonify([
        {"id": o.id, "name": o.name, "city": o.city}
        for o in orgs
    ])

@admin_bp.route("/approve/<int:id>", methods=["POST"])
def approve(id):
    org = Organization.query.get(id)

    if not org:
        return jsonify({"error": "Organization not found"}), 404

    org.approved = True
    db.session.commit()

    return jsonify({"message": "Organization approved"})
