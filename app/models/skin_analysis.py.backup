from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class SkinAnalysis(Base):
    __tablename__ = "skin_analyses"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_path = Column(String(255), nullable=False)

    # Treatment Program Scores
    hydration_score = Column(Float, nullable=False)
    elasticity_score = Column(Float, nullable=False)
    complexion_score = Column(Float, nullable=False)
    texture_score = Column(Float, nullable=False)

    # Skin Health Matrix Scores
    pores_score = Column(Float, nullable=False)
    eye_bags_score = Column(Float, nullable=False)
    acne_score = Column(Float, nullable=False)
    spots_score = Column(Float, nullable=False)
    redness_score = Column(Float, nullable=False)
    oiliness_score = Column(Float, nullable=False)
    wrinkles_score = Column(Float, nullable=False)
    skin_texture_score = Column(Float, nullable=False)

    # Enhanced Recommendations with structured routines
    am_routine = Column(JSON, nullable=True)  # Changed to JSON for structured data
    pm_routine = Column(JSON, nullable=True)  # Changed to JSON for structured data
    nutrition_recommendations = Column(Text, nullable=True)
    product_recommendations = Column(Text, nullable=True)
    ingredient_recommendations = Column(Text, nullable=True)

    # Timestamps
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="skin_analyses")

    @staticmethod
    def generate_scan_id():
        """Generate a unique scan ID"""
        return f"skin_scan_{uuid.uuid4().hex[:8]}"