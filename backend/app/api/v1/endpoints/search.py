from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Any
from app.core.database import get_db
from app.models.education.colleges import College
from app.models.education.schools import School
from app.models.stay.pg import PG
from app.models.stay.hostels import Hostel
from app.models.medical.hospital import Hospital
from app.schemas.search import GlobalSearchResult

router = APIRouter()

@router.get("/", response_model=List[GlobalSearchResult])
def global_search(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    Search across all entities: Colleges, Schools, Hostels, PGs, Hospitals, etc.
    """
    results = []
    
    # 1. Education
    colleges = db.query(College).filter(College.name.ilike(f"%{query}%")).limit(5).all()
    for item in colleges:
        results.append({"id": item.id, "name": item.name, "type": "college", "category": "Education", "image": item.image})
        
    schools = db.query(School).filter(School.name.ilike(f"%{query}%")).limit(5).all()
    for item in schools:
        results.append({"id": item.id, "name": item.name, "type": "school", "category": "Education", "image": item.image})

    # 2. Stay
    pgs = db.query(PG).filter(PG.name.ilike(f"%{query}%")).limit(5).all()
    for item in pgs:
        results.append({"id": item.id, "name": item.name, "type": "pg", "category": "Stay", "image": item.image})
        
    hostels = db.query(Hostel).filter(Hostel.name.ilike(f"%{query}%")).limit(5).all()
    for item in hostels:
        results.append({"id": item.id, "name": item.name, "type": "hostel", "category": "Stay", "image": item.image})

    # 3. Medical
    hospitals = db.query(Hospital).filter(Hospital.name.ilike(f"%{query}%")).limit(5).all()
    for item in hospitals:
        results.append({"id": item.id, "name": item.name, "type": "hospital", "category": "Medical", "image": item.image})

    return results
