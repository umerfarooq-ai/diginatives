from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

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

# AI Response Schema
class SkinAnalysisData(BaseModel):
    scanId: str
    treatmentProgram: TreatmentProgram
    skinHealthMatrix: SkinHealthMatrix
    amRoutine: str
    pmRoutine: str
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
    am_routine: str
    pm_routine: str
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
    am_routine: str
    pm_routine: str
    nutrition_recommendations: str
    product_recommendations: str
    ingredient_recommendations: str
    analysis_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True