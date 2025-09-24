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

# Treatment Program Schema
class TreatmentProgram(BaseModel):
    hydration: float
    elasticity: float
    complexion: float
    texture: float

# Skin Health Matrix Schema
class SkinHealthMatrix(BaseModel):
    pores: float
    underEyeAppearance: float
    blemishes: float
    spots: float
    redness: float
    oiliness: float
    fineLines: float
    texture: float

# Enhanced Routine Schema
class DetailedRoutine(BaseModel):
    steps: List[RoutineStep]

# AI Response Schema
class SkinAnalysisData(BaseModel):
    scanId: str
    treatmentProgram: TreatmentProgram
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
    hydration_score: float
    elasticity_score: float
    complexion_score: float
    texture_score: float
    pores_score: float
    eye_bags_score: float
    acne_score: float
    spots_score: float
    redness_score: float
    oiliness_score: float
    wrinkles_score: float
    skin_texture_score: float
    am_routine: Dict[str, Any]  # JSON data
    pm_routine: Dict[str, Any]  # JSON data
    nutrition_recommendations: str
    product_recommendations: str
    ingredient_recommendations: str

# Database Read Schema
class SkinAnalysisRead(BaseModel):
    id: int
    scan_id: str
    user_id: int
    image_path: str
    hydration_score: float
    elasticity_score: float
    complexion_score: float
    texture_score: float
    pores_score: float
    eye_bags_score: float
    acne_score: float
    spots_score: float
    redness_score: float
    oiliness_score: float
    wrinkles_score: float
    skin_texture_score: float
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