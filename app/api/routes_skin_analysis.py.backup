from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.crud import skin_analysis as crud_skin_analysis
from app.schemas.skin_analysis import SkinAnalysisResponse
from app.services.ai_skin_analysis import AISkinAnalysisService
import base64
import os
from datetime import datetime
from typing import Optional

router = APIRouter()
ai_service = AISkinAnalysisService()


@router.post("/skin-analysis", response_model=SkinAnalysisResponse)
async def analyze_skin(
        user_id: int = Form(...),
        analysis_date: Optional[str] = Form(None),
        image: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Analyze skin image using AI and return comprehensive results with detailed routines
    """

    # Validate user
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to analyze for this user")

    # Validate image file
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    if image.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Image file too large (max 10MB)")

    try:
        # Read and encode image
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')

        # Save image to disk
        upload_dir = "uploads/skin_images"
        os.makedirs(upload_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"skin_analysis_{user_id}_{timestamp}.jpg"
        image_path = os.path.join(upload_dir, filename)

        with open(image_path, "wb") as f:
            f.write(image_content)

        # Generate scan ID
        scan_id = crud_skin_analysis.generate_scan_id()

        # Analyze image with AI
        ai_result = ai_service.analyze_skin_image(image_base64)

        # Debug: Print the AI result structure
        print("AI Result Structure:")
        print(f"Keys in ai_result: {list(ai_result.keys())}")

        # Check if AI returned an error first
        if ai_result.get("error"):
            print(f"❌ AI Analysis failed: {ai_result.get('error_message')}")
            raise HTTPException(
                status_code=500,
                detail=f"AI Analysis failed: {ai_result.get('error_message')}"
            )

        # Only print treatment and matrix keys if they exist (not None)
        treatment = ai_result.get('treatmentProgram')
        matrix = ai_result.get('skinHealthMatrix')

        if treatment:
            print(f"treatmentProgram keys: {list(treatment.keys())}")
        else:
            print("treatmentProgram: None")

        if matrix:
            print(f"skinHealthMatrix keys: {list(matrix.keys())}")
        else:
            print("skinHealthMatrix: None")

        # Convert arrays to strings for database storage
        ai_result["productRecommendations"] = ai_service._convert_to_string(ai_result.get("productRecommendations", ""))
        ai_result["ingredientRecommendations"] = ai_service._convert_to_string(
            ai_result.get("ingredientRecommendations", ""))

        # Create skin analysis record with correct field mapping
        skin_analysis_data = {
            "scan_id": scan_id,
            "user_id": user_id,
            "image_path": image_path,
            "hydration_score": treatment["hydration"],
            "elasticity_score": treatment["elasticity"],
            "complexion_score": treatment["complexion"],
            "texture_score": treatment["texture"],
            "pores_score": matrix["pores"],
            "eye_bags_score": matrix["underEyeAppearance"],  # Map to database field
            "acne_score": matrix["blemishes"],  # Map to database field
            "spots_score": matrix["spots"],
            "redness_score": matrix["redness"],
            "oiliness_score": matrix["oiliness"],
            "wrinkles_score": matrix["fineLines"],  # Map to database field
            "skin_texture_score": matrix["texture"],
            "am_routine": ai_result.get("amRoutine", {}),  # Store as JSON
            "pm_routine": ai_result.get("pmRoutine", {}),  # Store as JSON
            "nutrition_recommendations": ai_result.get("nutritionRecommendations", ""),
            "product_recommendations": ai_result.get("productRecommendations", ""),
            "ingredient_recommendations": ai_result.get("ingredientRecommendations", "")
        }

        # Create and save to database
        from app.schemas.skin_analysis import SkinAnalysisCreate
        skin_analysis_create = SkinAnalysisCreate(**skin_analysis_data)
        crud_skin_analysis.create_skin_analysis(db, skin_analysis_create)

        # Prepare response with scan_id
        response_data = {
            "scanId": scan_id,
            "treatmentProgram": treatment,
            "skinHealthMatrix": matrix,
            "amRoutine": ai_result.get("amRoutine", {}),
            "pmRoutine": ai_result.get("pmRoutine", {}),
            "nutritionRecommendations": ai_result.get("nutritionRecommendations", ""),
            "productRecommendations": ai_result.get("productRecommendations", ""),
            "ingredientRecommendations": ai_result.get("ingredientRecommendations", "")
        }

        return SkinAnalysisResponse(
            success=True,
            data=response_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.get("/skin-analysis/{scan_id}")
async def get_skin_analysis(
        scan_id: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get skin analysis results by scan ID with detailed routines
    """
    skin_analysis = crud_skin_analysis.get_skin_analysis_by_scan_id(db, scan_id)

    if not skin_analysis:
        raise HTTPException(status_code=404, detail="Skin analysis not found")

    if skin_analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this analysis")

    response_data = {
        "scanId": skin_analysis.scan_id,
        "treatmentProgram": {
            "hydration": skin_analysis.hydration_score,
            "elasticity": skin_analysis.elasticity_score,
            "complexion": skin_analysis.complexion_score,
            "texture": skin_analysis.texture_score
        },
        "skinHealthMatrix": {
            "pores": skin_analysis.pores_score,
            "underEyeAppearance": skin_analysis.eye_bags_score,  # Map from database field
            "blemishes": skin_analysis.acne_score,  # Map from database field
            "spots": skin_analysis.spots_score,
            "redness": skin_analysis.redness_score,
            "oiliness": skin_analysis.oiliness_score,
            "fineLines": skin_analysis.wrinkles_score,  # Map from database field
            "texture": skin_analysis.skin_texture_score
        },
        "amRoutine": skin_analysis.am_routine or {"steps": []},
        "pmRoutine": skin_analysis.pm_routine or {"steps": []},
        "nutritionRecommendations": skin_analysis.nutrition_recommendations,
        "productRecommendations": skin_analysis.product_recommendations,
        "ingredientRecommendations": skin_analysis.ingredient_recommendations,
        "analysisDate": skin_analysis.analysis_date.isoformat() if skin_analysis.analysis_date else None
    }

    return SkinAnalysisResponse(
        success=True,
        data=response_data
    )


@router.get("/skin-analysis/user/{user_id}/history")
async def get_user_skin_analysis_history(
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get user's skin analysis history with routine summaries
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's history")

    analyses = crud_skin_analysis.get_skin_analyses_by_user_id(db, user_id, skip, limit)

    history_data = []
    for analysis in analyses:
        # Extract routine summaries
        am_routine_summary = "No AM routine available"
        pm_routine_summary = "No PM routine available"
        
        if analysis.am_routine and isinstance(analysis.am_routine, dict) and 'steps' in analysis.am_routine:
            am_steps = analysis.am_routine['steps']
            if am_steps:
                am_routine_summary = f"{len(am_steps)} steps: " + ", ".join([step.get('product_type', 'Unknown') for step in am_steps[:3]])
        
        if analysis.pm_routine and isinstance(analysis.pm_routine, dict) and 'steps' in analysis.pm_routine:
            pm_steps = analysis.pm_routine['steps']
            if pm_steps:
                pm_routine_summary = f"{len(pm_steps)} steps: " + ", ".join([step.get('product_type', 'Unknown') for step in pm_steps[:3]])

        history_data.append({
            "scanId": analysis.scan_id,
            "analysisDate": analysis.analysis_date.isoformat() if analysis.analysis_date else None,
            "treatmentProgram": {
                "hydration": analysis.hydration_score,
                "elasticity": analysis.elasticity_score,
                "complexion": analysis.complexion_score,
                "texture": analysis.texture_score
            },
            "skinHealthMatrix": {
                "pores": analysis.pores_score,
                "underEyeAppearance": analysis.eye_bags_score,
                "blemishes": analysis.acne_score,
                "spots": analysis.spots_score,
                "redness": analysis.redness_score,
                "oiliness": analysis.oiliness_score,
                "fineLines": analysis.wrinkles_score,
                "texture": analysis.skin_texture_score
            },
            "amRoutine": analysis.am_routine or {"steps": []},
            "pmRoutine": analysis.pm_routine or {"steps": []},
            "nutritionRecommendations": analysis.nutrition_recommendations,
            "productRecommendations": analysis.product_recommendations,
            "ingredientRecommendations": analysis.ingredient_recommendations,
            "amRoutineSummary": am_routine_summary,
            "pmRoutineSummary": pm_routine_summary
        })

    return {
        "success": True,
        "data": {
            "analyses": history_data,
            "total": len(history_data)
        }
    }