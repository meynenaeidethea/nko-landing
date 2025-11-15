from flask import Blueprint, request, jsonify
from backend.models import db, Organization

org_bp = Blueprint('organizations', __name__)

@org_bp.route('/', methods=['GET'])
def get_organizations():
    orgs = Organization.query.filter_by(approved=True).all()
    return jsonify([{
        "id": o.id,
        "name": o.name,
        "city": o.city,
        "category": o.category,
        "description": o.description,
        "phone": o.phone,
        "address": o.address,
        "website": o.website,
        "social_links": o.social_links,
        "lat": o.lat,
        "lon": o.lon
    } for o in orgs])

@org_bp.route('/', methods=['POST'])
def add_organization():
    data = request.json or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "Missing name"}), 400

    new_org = Organization(
        name=name,
        city=data.get("city"),
        category=data.get("category"),
        description=data.get("description"),
        phone=data.get("phone"),
        address=data.get("address"),
        website=data.get("website"),
        social_links=data.get("social_links"),
        lat=data.get("lat"),
        lon=data.get("lon"),
        approved=False
    )
    db.session.add(new_org)
    db.session.commit()
    return jsonify({"message": "Organization added, awaiting approval"}), 201
