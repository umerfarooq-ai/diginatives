from sqlalchemy.orm import Session
from app.models.skin_analysis import SkinAnalysis
from app.schemas.skin_analysis import SkinAnalysisCreate, SkinAnalysisRead
from typing import List, Optional
import uuid

def create_skin_analysis(db: Session, skin_analysis: SkinAnalysisCreate) -> SkinAnalysis:
    """Create a new skin analysis record"""
    db_skin_analysis = SkinAnalysis(**skin_analysis.dict())
    db.add(db_skin_analysis)
    db.commit()
    db.refresh(db_skin_analysis)
    return db_skin_analysis

def get_skin_analysis_by_scan_id(db: Session, scan_id: str) -> Optional[SkinAnalysis]:
    """Get skin analysis by scan ID"""
    return db.query(SkinAnalysis).filter(SkinAnalysis.scan_id == scan_id).first()

def get_skin_analyses_by_user_id(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[SkinAnalysis]:
    """Get user's skin analysis history"""
    return db.query(SkinAnalysis)\
        .filter(SkinAnalysis.user_id == user_id)\
        .order_by(SkinAnalysis.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_skin_analysis_by_id(db: Session, analysis_id: int) -> Optional[SkinAnalysis]:
    """Get skin analysis by ID"""
    return db.query(SkinAnalysis).filter(SkinAnalysis.id == analysis_id).first()

def delete_skin_analysis(db: Session, analysis_id: int) -> bool:
    """Delete a skin analysis record"""
    skin_analysis = db.query(SkinAnalysis).filter(SkinAnalysis.id == analysis_id).first()
    if skin_analysis:
        db.delete(skin_analysis)
        db.commit()
        return True
    return False

def generate_scan_id() -> str:
    """Generate a unique scan ID"""
    return f"skin_scan_{uuid.uuid4().hex[:8]}"