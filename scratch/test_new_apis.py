import os
import sys
import json
from sqlmodel import Session, select
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.db import get_session
from app.models.domain import Opportunity, FarmerProfile, UserProfile, Document
from app.services.eligibility import EligibilityEngine

engine = EligibilityEngine()
session = next(get_session())
user_id = 10
farmer_profile = session.exec(select(FarmerProfile).where(FarmerProfile.user_id==user_id)).first()
user_profile = session.exec(select(UserProfile).where(UserProfile.user_id==user_id)).first()

user_dict = {
    'id': user_id,
    'income': farmer_profile.annual_income,
    'age': user_profile.age,
    'category': user_profile.category,
    'state': user_profile.state,
    'land_area': farmer_profile.land_size_acres,
    'gender': user_profile.gender
}

opps = session.exec(select(Opportunity).where(Opportunity.module=='farmer')).all()
for opp in opps:
    rules = opp.eligibility_rules if isinstance(opp.eligibility_rules, dict) else (json.loads(opp.eligibility_rules) if opp.eligibility_rules else {})
    docs = opp.required_documents if isinstance(opp.required_documents, list) else (json.loads(opp.required_documents) if opp.required_documents else [])
    
    opp_dict = {
        'id': opp.id,
        'title': opp.title,
        'eligibility_rules': rules,
        'required_documents': docs
    }
    
    verdict = engine.evaluate_single_eligibility(user_dict, [], opp_dict)
    print(verdict)
