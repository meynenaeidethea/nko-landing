from flask import Blueprint, request, jsonify
from backend.models import Organization, db
from backend.utils.jwt_utils import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/pending', methods=['GET'])
@admin_required
def get_pending_organizations():
    pending_orgs = Organization.query.filter_by(approved=False).all()
    return jsonify([{
        'id': org.id,
        'name': org.name,
        'city': org.city,
        'category': org.category,
        'description': org.description
    } for org in pending_orgs])

@admin_bp.route('/approve/<int:org_id>', methods=['POST'])
@admin_required
def approve_organization(org_id):
    org = Organization.query.get_or_404(org_id)
    org.approved = True
    db.session.commit()
    return jsonify({'message': 'Organization approved'})

@admin_bp.route('/reject/<int:org_id>', methods=['POST'])
@admin_required
def reject_organization(org_id):
    org = Organization.query.get_or_404(org_id)
    db.session.delete(org)
    db.session.commit()
    return jsonify({'message': 'Organization rejected'})