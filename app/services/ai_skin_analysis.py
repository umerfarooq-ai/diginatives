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
            "treatmentProgram": {
                "hydration": float (0-100),
                "elasticity": float (0-100),
                "complexion": float (0-100),
                "texture": float (0-100)
            },
            "skinHealthMatrix": {
                "pores": float (0-100),
                "underEyeAppearance": float (0-100), 
                "blemishes": float (0-100),
                "spots": float (0-100),
                "redness": float (0-100),
                "oiliness": float (0-100),
                "fineLines": float (0-100),
                "texture": float (0-100)
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
            - Return only the JSON. Do not include explanations outside the JSON.
            """

            # Convert base64 to bytes for Gemini
            image_bytes = base64.b64decode(image_base64)

            # Call Gemini Vision API
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            ])

            # Get the response content
            ai_response = response.text
            print("Gemini RAW OUTPUT:\n", ai_response)

            # Try to parse as JSON first
            try:
                # Extract JSON from the response if it's wrapped in markdown
                json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object in the response
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = ai_response

                result = json.loads(json_str)
                
                # Validate and clean routine descriptions
                result = self._validate_routine_descriptions(result)
                
                return result

            except json.JSONDecodeError:
                print("JSON parsing failed, using text parser")
                return self._parse_field_lines(ai_response)

        except Exception as e:
            print(f"❌ Error in Gemini analysis: {e}")
            print("🔄 Using fallback response...")
            return self._get_error_response(str(e))

    def _validate_routine_descriptions(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean routine descriptions to ensure they're under 40 words
        """
        # Validate AM routine
        if 'amRoutine' in result and 'steps' in result['amRoutine']:
            for step in result['amRoutine']['steps']:
                if 'description' in step:
                    step['description'] = self._truncate_description(step['description'])
        
        # Validate PM routine
        if 'pmRoutine' in result and 'steps' in result['pmRoutine']:
            for step in result['pmRoutine']['steps']:
                if 'description' in step:
                    step['description'] = self._truncate_description(step['description'])
        
        return result

    def _truncate_description(self, description: str, max_words: int = 40) -> str:
        """
        Truncate description to maximum number of words
        """
        words = description.split()
        if len(words) <= max_words:
            return description
        return ' '.join(words[:max_words]) + '...'

    def _parse_field_lines(self, text: str) -> Dict[str, Any]:
        """
        Parse AI response text and extract structured data with enhanced routines
        """
        try:
            result = {
                "treatmentProgram": {
                    "hydration": 70.0,
                    "elasticity": 65.0,
                    "complexion": 75.0,
                    "texture": 70.0
                },
                "skinHealthMatrix": {
                    "pores": 60.0,
                    "underEyeAppearance": 50.0,
                    "blemishes": 40.0,
                    "spots": 0.0,
                    "redness": 45.0,
                    "oiliness": 65.0,
                    "fineLines": 40.0,
                    "texture": 70.0
                },
                "amRoutine": {
                    "steps": [
                        {
                            "step_number": 1,
                            "product_type": "Gentle Facial Cleanser",
                            "description": "Remove dirt and oil with a gentle cleanser. Apply in circular motions and rinse with lukewarm water."
                        },
                        {
                            "step_number": 2,
                            "product_type": "Antioxidant Serum",
                            "description": "Apply antioxidant serum to brighten skin and protect from environmental damage. Use 2-3 drops."
                        },
                        {
                            "step_number": 3,
                            "product_type": "Lightweight Moisturizer",
                            "description": "Hydrate skin with a lightweight moisturizer. Gently pat until fully absorbed."
                        },
                        {
                            "step_number": 4,
                            "product_type": "Broad-Spectrum SPF",
                            "description": "Protect skin with broad-spectrum SPF 30+. Apply generously and reapply every 2 hours."
                        }
                    ]
                },
                "pmRoutine": {
                    "steps": [
                        {
                            "step_number": 1,
                            "product_type": "Double Cleanse System",
                            "description": "First remove makeup with oil cleanser, then cleanse with gentle face wash for clean skin."
                        },
                        {
                            "step_number": 2,
                            "product_type": "Targeted Treatment Serum",
                            "description": "Apply targeted serum for your skin concerns. Let it absorb before next step."
                        },
                        {
                            "step_number": 3,
                            "product_type": "Night Repair Moisturizer",
                            "description": "Use richer moisturizer for overnight repair. Apply in upward motions."
                        }
                    ]
                },
                "nutritionRecommendations": "Stay hydrated, eat antioxidant-rich foods, reduce sugar intake",
                "productRecommendations": "Gentle cleanser, Vitamin C, Retinol, Moisturizer, SPF",
                "ingredientRecommendations": "Hyaluronic acid, Vitamin C, Retinol, Niacinamide"
            }

            # Try to extract scores from the text
            lines = text.split('\n')
            for line in lines:
                line = line.strip().lower()

                # Extract hydration score
                if 'hydration' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["hydration"] = score

                # Extract elasticity score
                elif 'elasticity' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["elasticity"] = score

                # Extract complexion score
                elif 'complexion' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["complexion"] = score

                # Extract texture score
                elif 'texture' in line:
                    score = self._extract_score_from_line(line)
                    if score is not None:
                        result["treatmentProgram"]["texture"] = score

                # Extract skin health matrix scores
                elif any(keyword in line for keyword in
                         ['pores', 'under eye', 'blemishes', 'spots', 'redness', 'oiliness', 'fine lines']):
                    for keyword in ['pores', 'under eye', 'blemishes', 'spots', 'redness', 'oiliness', 'fine lines']:
                        if keyword in line:
                            score = self._extract_score_from_line(line)
                            if score is not None:
                                if keyword == 'under eye':
                                    result["skinHealthMatrix"]["underEyeAppearance"] = score
                                elif keyword == 'fine lines':
                                    result["skinHealthMatrix"]["fineLines"] = score
                                elif keyword == 'blemishes':
                                    result["skinHealthMatrix"]["blemishes"] = score
                                else:
                                    result["skinHealthMatrix"][keyword] = score
                            break

            return result

        except Exception as e:
            print(f"Text parsing failed: {e}")
            return self._get_fallback_response()

    def _extract_score_from_line(self, line: str) -> float:
        """
        Extract a score (0-100) from a text line
        """
        try:
            # Look for numbers in the line
            numbers = re.findall(r'\d+(?:\.\d+)?', line)
            for num in numbers:
                score = float(num)
                if 0 <= score <= 100:
                    return score
            return None
        except:
            return None

    def _get_fallback_response(self) -> Dict[str, Any]:
        """
        Return a fallback response if AI analysis fails
        """
        print("📋 Returning fallback response for testing")
        return {
            "treatmentProgram": {
                "hydration": 70.0,
                "elasticity": 65.0,
                "complexion": 75.0,
                "texture": 70.0
            },
            "skinHealthMatrix": {
                "pores": 60.0,
                "underEyeAppearance": 50.0,
                "blemishes": 40.0,
                "spots": 0.0,
                "redness": 45.0,
                "oiliness": 65.0,
                "fineLines": 40.0,
                "texture": 70.0
            },
            "amRoutine": {
                "steps": [
                    {
                        "step_number": 1,
                        "product_type": "Gentle Facial Cleanser",
                        "description": "FALLBACK: Cleanse face with gentle cleanser to remove impurities and prepare skin."
                    },
                    {
                        "step_number": 2,
                        "product_type": "Antioxidant Serum",
                        "description": "FALLBACK: Apply antioxidant serum to brighten and protect skin from damage."
                    },
                    {
                        "step_number": 3,
                        "product_type": "Lightweight Moisturizer",
                        "description": "FALLBACK: Hydrate skin with lightweight moisturizer for all-day comfort."
                    },
                    {
                        "step_number": 4,
                        "product_type": "Broad-Spectrum SPF",
                        "description": "FALLBACK: Protect with broad-spectrum sunscreen to prevent sun damage."
                    }
                ]
            },
            "pmRoutine": {
                "steps": [
                    {
                        "step_number": 1,
                        "product_type": "Double Cleanse System",
                        "description": "FALLBACK: Remove makeup and cleanse thoroughly for clean skin."
                    },
                    {
                        "step_number": 2,
                        "product_type": "Targeted Treatment Serum",
                        "description": "FALLBACK: Apply targeted treatment for your specific skin concerns."
                    },
                    {
                        "step_number": 3,
                        "product_type": "Night Repair Moisturizer",
                        "description": "FALLBACK: Use nourishing night cream for overnight repair and hydration."
                    }
                ]
            },
            "nutritionRecommendations": "FALLBACK: General nutrition advice (AI analysis failed)",
            "productRecommendations": "FALLBACK: Basic products (AI analysis failed)",
            "ingredientRecommendations": "FALLBACK: Common ingredients (AI analysis failed)",
            "fallback_message": "⚠️ AI ANALYSIS FAILED - This is fallback data for testing"
        }

    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Return error response with actual error message
        """
        print(f"📋 Returning error response: {error_message}")
        return {
            "error": True,
            "error_message": f"AI Analysis Failed: {error_message}",
            "treatmentProgram": {},
            "skinHealthMatrix": {},
            "amRoutine": {"steps": []},
            "pmRoutine": {"steps": []},
            "nutritionRecommendations": "",
            "productRecommendations": "",
            "ingredientRecommendations": ""
        }

    def _convert_to_string(self, value) -> str:
        """
        Convert value to string, handling both strings and lists
        """
        if isinstance(value, list):
            return ", ".join(value)
        elif isinstance(value, str):
            return value
        else:
            return str(value) 