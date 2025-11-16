from flask import Blueprint, request, jsonify
from backend.models import Organization, db
from backend.utils.jwt_utils import token_required

org_bp = Blueprint('organizations', __name__)

@org_bp.route('/', methods=['GET'])
def get_organizations():
    # Возвращаем только подтвержденные организации
    orgs = Organization.query.filter_by(approved=True).all()
    return jsonify([{
        'id': org.id,
        'name': org.name,
        'city': org.city,
        'category': org.category,
        'description': org.description,
        'phone': org.phone,
        'address': org.address,
        'website': org.website,
        'social_links': org.social_links,
        'lat': org.lat,
        'lon': org.lon
    } for org in orgs])

@org_bp.route('/', methods=['POST'])
@token_required
def create_organization():
    try:
        # Проверяем, есть ли у пользователя уже организация
        existing_org = Organization.query.filter_by(user_id=request.current_user.id).first()
        if existing_org:
            return jsonify({'error': 'У вас уже есть организация. Один пользователь может добавить только одну организацию.'}), 400
        
        data = request.get_json()
        
        org = Organization(
            name=data.get('name'),
            city=data.get('city'),
            category=data.get('category'),
            description=data.get('description'),
            phone=data.get('phone'),
            address=data.get('address'),
            website=data.get('website'),
            social_links=data.get('social_links'),
            lat=data.get('lat'),
            lon=data.get('lon'),
            approved=False,  # новая организация требует модерации
            user_id=request.current_user.id  # связываем с пользователем
        )
        
        db.session.add(org)
        db.session.commit()
        
        return jsonify({'message': 'Organization created and pending approval', 'id': org.id}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@org_bp.route('/my', methods=['GET'])
@token_required
def get_my_organizations():
    orgs = Organization.query.filter_by(user_id=request.current_user.id).all()
    return jsonify([{
        'id': org.id,
        'name': org.name,
        'city': org.city,
        'category': org.category,
        'description': org.description,
        'phone': org.phone,
        'address': org.address,
        'website': org.website,
        'social_links': org.social_links,
        'lat': org.lat,
        'lon': org.lon,
        'approved': org.approved
    } for org in orgs])