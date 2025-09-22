from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

# New Routine Step Schema
class RoutineStep(BaseModel):
    step_number: int
    product_type: str
    description: str  # Max 40 words

# Request Schemas
class SkinAnalysisRequest(BaseModel):
    user_id: int
    analysis_date: Optional[str] = None

# Skin Health Matrix Schema
class SkinHealthMatrix(BaseModel):
    moisture: float
    texture: float
    acne: float
    dryness: float
    elasticity: float
    complexion: float
    skin_age: float

# Enhanced Routine Schema
class DetailedRoutine(BaseModel):
    steps: List[RoutineStep]

# AI Response Schema
class SkinAnalysisData(BaseModel):
    scanId: str
    skinHealthMatrix: SkinHealthMatrix
    amRoutine: DetailedRoutine
    pmRoutine: DetailedRoutine
    nutritionRecommendations: str
    productRecommendations: str
    ingredientRecommendations: str

# API Response Schema
class SkinAnalysisResponse(BaseModel):
    success: bool
    data: SkinAnalysisData

# Database Create Schema
class SkinAnalysisCreate(BaseModel):
    scan_id: str
    user_id: int
    image_path: str
    moisture_score: float
    texture_score: float
    acne_score: float
    dryness_score: float
    elasticity_score: float
    complexion_score: float
    skin_age_score: float
    am_routine: Dict[str, Any]
    pm_routine: Dict[str, Any]
    nutrition_recommendations: str
    product_recommendations: str
    ingredient_recommendations: str

# Database Read Schema
class SkinAnalysisRead(BaseModel):
    id: int
    scan_id: str
    user_id: int
    image_path: str
    moisture_score: float
    texture_score: float
    acne_score: float
    dryness_score: float
    elasticity_score: float
    complexion_score: float
    skin_age_score: float
    am_routine: Optional[Dict[str, Any]]
    pm_routine: Optional[Dict[str, Any]]
    nutrition_recommendations: str
    product_recommendations: str
    ingredient_recommendations: str
    analysis_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
