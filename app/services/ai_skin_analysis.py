import os
import base64
import google.generativeai as genai
from typing import Dict, Any, List
import json
import re
from dotenv import load_dotenv

load_dotenv()


class AISkinAnalysisService:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_skin_image(self, image_base64: str) -> Dict[str, Any]:
        """
        Analyze skin image using Google Gemini Vision API
        """
        try:
            # Create the prompt for skin analysis with detailed routines
            prompt = """
            Analyze this skin image and provide a comprehensive, non-medical cosmetic skincare assessment.

            Please return the results in the following structured JSON format:

            {
            "skinHealthMatrix": {
                "moisture": float (0-100),
                "texture": float (0-100),
                "acne": float (0-100),
                "dryness": float (0-100),
                "elasticity": float (0-100),
                "complexion": float (0-100),
                "skin_age": float (actual age the skin appears to be)
            },
            "amRoutine": {
                "steps": [
                    {
                        "step_number": 1,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of why this product is recommended and how to apply (max 40 words)"
                    },
                    {
                        "step_number": 2,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of benefits and application method (max 40 words)"
                    },
                    {
                        "step_number": 3,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of hydration benefits and application (max 40 words)"
                    },
                    {
                        "step_number": 4,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of sun protection importance and application (max 40 words)"
                    }
                ]
            },
            "pmRoutine": {
                "steps": [
                    {
                        "step_number": 1,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of removing makeup and impurities (max 40 words)"
                    },
                    {
                        "step_number": 2,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of active ingredients and benefits (max 40 words)"
                    },
                    {
                        "step_number": 3,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of overnight repair and application (max 40 words)"
                    },
                    {
                        "step_number": 4,
                        "product_type": "AI-determined product based on skin analysis",
                        "description": "Brief description of final hydration and skin barrier support (max 40 words)"
                    }
                ]
            },
            "nutritionRecommendations": "short string of general dietary advice",
            "productRecommendations": "list of product types, not brands",
            "ingredientRecommendations": "list of common skincare ingredients"
            }

            Guidelines:
            - This is not a medical diagnosis.
            - Do not mention or infer medical conditions.
            - Each routine step description must be MAXIMUM 40 words.
            - Make descriptions practical and actionable.
            - Focus on cosmetic benefits and general skincare advice.
            - Choose product types based on the skin analysis results (e.g., if skin is dry, suggest hydrating products; if oily, suggest oil-control products).
            - Product types should be specific but not brand names (e.g., "Hydrating Cleanser", "Vitamin C Serum", "Oil-Free Moisturizer", "Broad-Spectrum SPF").
            - BOTH AM and PM routines must have exactly 4 steps each.
            - Return only the JSON. Do not include explanations outside the JSON.
            """

            # Convert base64 to image data
            image_data = base64.b64decode(image_base64)
            
            # Create the image part for the model
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }
            
            # Generate content with the model
            response = self.model.generate_content([prompt, image_part])
            
            # Extract and parse the JSON response
            ai_result = self._parse_ai_response(response.text)
            
            # Validate routine descriptions
            ai_result = self._validate_routine_descriptions(ai_result)
            
            return ai_result
            
        except Exception as e:
            print(f"Error in AI skin analysis: {str(e)}")
            return self._get_fallback_response()

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the AI response and extract JSON data
        """
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                ai_result = json.loads(json_str)
                
                # Debug: Print the structure
                print("AI Result Structure:")
                print(f"Keys in ai_result: {list(ai_result.keys())}")
                if 'skinHealthMatrix' in ai_result:
                    print(f"skinHealthMatrix keys: {list(ai_result['skinHealthMatrix'].keys())}")
                
                return ai_result
            else:
                print("No JSON found in AI response")
                return self._get_fallback_response()
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return self._get_fallback_response()
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
            return self._get_fallback_response()

    def _validate_routine_descriptions(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and truncate routine descriptions to ensure they are under 40 words
        """
        for routine_type in ['amRoutine', 'pmRoutine']:
            if routine_type in ai_result and 'steps' in ai_result[routine_type]:
                for step in ai_result[routine_type]['steps']:
                    if 'description' in step:
                        step['description'] = self._truncate_description(step['description'])
        
        return ai_result

    def _truncate_description(self, description: str) -> str:
        """
        Truncate description to maximum 40 words
        """
        words = description.split()
        if len(words) > 40:
            return ' '.join(words[:40]) + "..."
        return description

    def _get_fallback_response(self) -> Dict[str, Any]:
        """
        Return a fallback response when AI analysis fails
        """
        return {
            "skinHealthMatrix": {
                "moisture": 50.0,
                "texture": 50.0,
                "acne": 50.0,
                "dryness": 50.0,
                "elasticity": 50.0,
                "complexion": 50.0,
                "skin_age": 30.0
            },
            "amRoutine": {
                "steps": [
                    {
                        "step_number": 1,
                        "product_type": "Gentle Cleanser",
                        "description": "Gently cleanse skin with lukewarm water, avoiding harsh scrubbing. Rinse thoroughly and pat dry."
                    },
                    {
                        "step_number": 2,
                        "product_type": "Lightweight Moisturizer",
                        "description": "Apply a thin layer of moisturizer to hydrate and protect skin. Use gentle upward strokes."
                    },
                    {
                        "step_number": 3,
                        "product_type": "Vitamin C Serum",
                        "description": "Apply a small amount of serum to brighten skin and provide antioxidant protection. Use gentle patting motions."
                    },
                    {
                        "step_number": 4,
                        "product_type": "Broad-Spectrum SPF 30",
                        "description": "Apply sunscreen liberally to protect skin from sun damage. Reapply every two hours when outdoors."
                    }
                ]
            },
            "pmRoutine": {
                "steps": [
                    {
                        "step_number": 1,
                        "product_type": "Oil-Free Makeup Remover",
                        "description": "Remove makeup and cleanse skin thoroughly using a gentle, oil-free makeup remover. Massage gently and rinse."
                    },
                    {
                        "step_number": 2,
                        "product_type": "Gentle Cleanser",
                        "description": "Follow with a gentle cleanser to remove any remaining impurities. Use circular motions and rinse thoroughly."
                    },
                    {
                        "step_number": 3,
                        "product_type": "Night Cream",
                        "description": "Apply a thin layer of night cream to help repair and rejuvenate skin overnight. Use gentle upward strokes."
                    },
                    {
                        "step_number": 4,
                        "product_type": "Eye Cream",
                        "description": "Apply a small amount of eye cream around the eye area using your ring finger. Pat gently until absorbed."
                    }
                ]
            },
            "nutritionRecommendations": "Eat a balanced diet rich in fruits, vegetables, and whole grains; limit processed foods and sugar.",
            "productRecommendations": ["Gentle Cleanser", "Lightweight Moisturizer", "Vitamin C Serum", "Broad-Spectrum SPF 30", "Oil-Free Makeup Remover", "Night Cream", "Eye Cream"],
            "ingredientRecommendations": ["Vitamin C", "Hyaluronic Acid", "Niacinamide", "Retinol", "Peptides"]
        }

    def _convert_to_string(self, data):
        """
        Convert data to string format for database storage
        """
        if isinstance(data, list):
            return ", ".join(data)
        return str(data)
